"""Script to create executable with help of :mod:`cx_Freeze`.

Needed mostly because of reletive imports, otherwise could've called ``svg2ssa\__main__.py`` directly.
"""

from svg2ssa.__main__ import cli

cli()
