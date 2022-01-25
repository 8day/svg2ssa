literals = "MmLlHhVvCcSsQqTt"  # All SVG commands

tokens = ("NMB",)

t_ignore_WSP = r"[ \t\n\r]"
t_ignore_COMMA = r","
t_ignore_CLOSE_PATH = r"[Zz]"


def t_NMB(t):
    """[+-]?(?:(?:(?:[0-9]+)?\.(?:[0-9]+)|(?:[0-9]+)\.)(?:[eE][+-]?(?:[0-9]+))?|(?:[0-9]+)(?:[eE][+-]?(?:[0-9]+)))|[+-]?(?:[0-9]+)"""
    t.value = float(t.value)
    return t


def t_error(t):
    # Fixme: when t.value[0] will be the last character in the sequence, t.value[1:11] may cause errors.
    raise Exception(
        'The next illegal character were found in "d" attribute: "{0}".\n'
        "These characters were right after it: {1}".format(t.value[0], t.value[1:11])
    )
