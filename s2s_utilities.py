import re


# Code below is slightly modified SVG path BNF for coordinates.
# digit_sequence = r'(?:[0-9]+)'
# sign = r'[+-]'
# exponent = f'(?:[eE]{sign}?{digit_sequence})'
# fractional_constant = f'(?:{digit_sequence}?\\.{digit_sequence}|{digit_sequence}\\.)'
# floating_point_constant = f'(?:{fractional_constant}{exponent}?|{digit_sequence}{exponent})'
# integer_constant = digit_sequence
# Order was swapped because of ambiguity: float is int w/o fraction, but can be
# changed to f'{sign}?(?:{floating_point_constant}|{integer_constant})' since 'sign' present in both cases.
# number = f'{sign}?{floating_point_constant}|{sign}?{integer_constant}'
number = r"[+-]?(?:(?:(?:[0-9]+)?\.(?:[0-9]+)|(?:[0-9]+)\.)(?:[eE][+-]?(?:[0-9]+))?|(?:[0-9]+)(?:[eE][+-]?(?:[0-9]+)))|[+-]?(?:[0-9]+)"
length_number = re.compile(f"^({number})$")
length_units = re.compile(f"^({number})(px|pt|pc|cm|mm|in)$", re.I)


def convert_svglength_to_pixels(data):
    """Converts <length> to its respective pixel equivalent @90dpi,
    which is in accordance with CSS standard.
    """

    # Fixme: should support '%' as well! (Read <length> spec.)
    # Note: factors for transforming were taken from Inkscape SVGLoader.py.
    # Note: currently these units is unsupported:
    # o. em (relative to CSS "font-size");
    # o. ex (relative to font x-height).

    if length_number.search(data):
        data = float(data)
    elif length_units.search(data):
        search_result = length_units.search(data)
        length = float(search_result.group(1))
        unit = search_result.group(2).lower()
        if unit == "px":
            data = length
        elif unit == "pt":
            data = length * 1.25
        elif unit == "pc":
            data = length * 15
        elif unit == "mm":
            data = length * 9
        elif unit == "cm":
            data = length * 90
        elif unit == "in":
            data = length * 90
    else:
        raise TypeError(f"Wrong length unit! String that caused the error contained this: '{data!s}'.")
    return data


def collapse_consecutive_objects(list_of_objects):

    # Alt. name: grouping (summ) similar objects in a sequence (when sequence length is predefined and it shouldn't change).
    # Do not modify!
    # In its current form (i.e. two iterations instead of one)
    # algorithm below is *significantly* less complex & very
    # general, which makes it ideal for use in everyday life.

    if len(list_of_objects) > 1:
        for i in range(len(list_of_objects) - 1):
            curr = list_of_objects[i]
            next = list_of_objects[i + 1]
            if curr.dtype == next.dtype:
                list_of_objects[i + 1] = curr + next
                list_of_objects[i] = None
        for i in range(len(list_of_objects) - 1, -1, -1):
            if list_of_objects[i] is None:
                del list_of_objects[i]
    return list_of_objects


def collapse_consecutive_objects_alternative_01(list_of_objects):
    if len(list_of_objects) > 1:
        l = len(list_of_objects) - 1
        i = 0
        while i < l:
            curr = list_of_objects[i]
            next = list_of_objects[i + 1]
            if curr.dtype == next.dtype:
                list_of_objects[i + 1] = curr + next
                del list_of_objects[i]
                l -= 1
            i += 1
    return list_of_objects


trafos_all = {"matrix", "skewX", "skewY", "scale", "translate", "rotate"}
trafos_unsupported = {"matrix", "skewX", "skewY"}


def collapse_unnecessary_trafos(list_of_trafos, unnecessary_transformations):
    """Finds repeated, unconsecutive trafos and then collapses
    everything inbetween into the matrix (this is handled by trafos themselves).
    """

    trafos_unnecessary = trafos_all & unnecessary_transformations | trafos_unsupported
    trafos_all_without_unnecessary = trafos_all - trafos_unnecessary

    # Create dictionary with trafos indeces.
    dictionary = {}
    for i, trafo in enumerate(list_of_trafos):
        if trafo.dtype in dictionary:
            dictionary[trafo.dtype].append(i)
        else:
            dictionary[trafo.dtype] = [i]

    # Find index of the furthest unsupported by SSA trafo.
    # Note: by design, the largest idx should be last (since there was no
    # sorting/shuffle applied), so "max(dictionary[trafo])" should be equal
    # to "dictionary[trafo][-1]".
    idx_unnec = -1
    for trafo in trafos_unnecessary:
        if trafo in dictionary and dictionary[trafo][-1] > idx_unnec:
            idx_unnec = dictionary[trafo][-1]

    # Find index of the furthest repetitive and unconsecutive trafo.
    # Note: 'trafos_all_without_unnecessary' *may* be an empty set, it is
    # completely acceptable.
    idx_repet = -1
    for trafo in trafos_all_without_unnecessary:
        if (
            trafo in dictionary
            and len(dictionary[trafo]) > 1
            and dictionary[trafo][-2] > idx_repet
        ):
            # Implies that indeces are in the "right" order, i.e. not shuffled.
            # Inside this function it is always true.
            idx_repet = dictionary[trafo][-2]

    # Merge trafos, if need be.
    if idx_unnec != -1 or idx_repet != -1:
        # Note: "+1" for making interval inclusive: [n,m] instead of [n,m).
        idx = (idx_unnec if idx_unnec > idx_repet else idx_repet) + 1
        acc = list_of_trafos[0]
        for i in range(1, idx):
            acc += list_of_trafos[i]
        list_of_trafos[:idx] = [acc]

    return list_of_trafos
