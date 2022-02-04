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
