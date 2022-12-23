"""Script required for relative paths mechanism.

Both :mod:`py2exe` and :mod:`cx_Freeze` require it, which implies that it's hard to bypass it.

Warning:

    Turns out script for booting of the package with relative imports must be in same dir as the package itself (hacking sys.path doesn't help, as that code is than baked into frozen release).
"""


from svg2ssa.__main__ import cli

cli()
