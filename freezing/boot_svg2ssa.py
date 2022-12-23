"""Script required for relative paths mechanism.

Both :mod:`py2exe` and :mod:`cx_Freeze` require it, which implies that it's hard to bypass it.
"""


from svg2ssa.__main__ import cli

cli()
