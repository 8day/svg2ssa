literals = r"()"

reserved = {
    "matrix": "MATRIX",
    "translate": "TRANSLATE",
    "scale": "SCALE",
    "rotate": "ROTATE",
    "skewX": "SKEWX",
    "skewY": "SKEWY",
}

tokens = ("NMB",) + tuple(reserved.values())

t_ignore_WSP = r"[ \t\n\r]"
t_ignore_COMMA = r","


def t_ID(t):
    r"[a-zA-Z]{5,}"
    t.type = reserved.get(t.value)
    if not t.type:  # Checks whether found word was one from 'reserved'.
        t_error(t)
    return t


def t_NMB(t):
    """[+-]?(?:(?:(?:[0-9]+)?\.(?:[0-9]+)|(?:[0-9]+)\.)(?:[eE][+-]?(?:[0-9]+))?|(?:[0-9]+)(?:[eE][+-]?(?:[0-9]+)))|[+-]?(?:[0-9]+)"""
    t.value = float(t.value)
    return t


def t_error(t):
    # Fixme: when t.value[0] will be the last character in the sequence, t.value[1:11] may cause errors.
    raise Exception(
        'The next illegal character were found in "transformation" attribute: "{0}".\n'
        "These characters were right after it: {1}".format(t.value[0], t.value[1:11])
    )
