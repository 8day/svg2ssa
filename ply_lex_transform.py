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
    # Checks whether found word was one from ``reserved``.
    if not t.type:
        t_error(t)
    return t


def t_NMB(t):
    """[+-]?(?:(?:(?:[0-9]+)?\.(?:[0-9]+)|(?:[0-9]+)\.)(?:[eE][+-]?(?:[0-9]+))?|(?:[0-9]+)(?:[eE][+-]?(?:[0-9]+)))|[+-]?(?:[0-9]+)"""
    t.value = float(t.value)
    return t


def t_error(t):
    # Fixme: When ``t.value[0]`` will be the last character in the sequence, ``t.value[1:11]`` may cause errors.
    raise Exception(
        f"The next illegal character were found in 'transformation' attribute: '{t.value[0]}'.\n"
        f"These characters were right after it: {t.value[1:11]}"
    )
