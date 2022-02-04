# All SVG commands.
literals = "MmLlHhVvCcSsQqTt"

tokens = ("NMB",)

t_ignore_WSP = r"[ \t\n\r]"
t_ignore_COMMA = r","
t_ignore_CLOSE_PATH = r"[Zz]"


def t_NMB(t):
    """[+-]?(?:(?:(?:[0-9]+)?\.(?:[0-9]+)|(?:[0-9]+)\.)(?:[eE][+-]?(?:[0-9]+))?|(?:[0-9]+)(?:[eE][+-]?(?:[0-9]+)))|[+-]?(?:[0-9]+)"""
    t.value = float(t.value)
    return t


def t_error(t):
    # Fixme: When ``t.value[0]`` will be the last character in the sequence, ``t.value[1:11]`` may cause errors.
    raise Exception(
        f"The next illegal character were found in 'd' attribute: '{t.value[0]}'.\n"
        f"These characters were right after it: {t.value[1:11]}"
    )
