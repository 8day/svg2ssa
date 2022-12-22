"""Script to create executable with help of :mod:`cx_Freeze`.

Needed mostly because of reletive imports, otherwise could've called ``svg2ssa\__main__.py`` directly.

To cx_Freeze:

1. run ``pip install cx-Freeze`` to install cx_Freeze. **Note that it may not support your version of Python (it will error out upon installation from PyPI), therefore you may need to use older version. E.g., cx_Freeze 6.13.0 doesn't support Python 3.11.1, unlike 3.10.9**;
2. un-/comment necessary lines in ``document.py`` import section;
3. run ``python\Scripts\cxfreeze.exe .\cxfreeze.py --icon=.\logo.ico --target-name=svg2ssa --target-dir=.\dist\svg2ssa-{xml_parser}-{version}`` inside svg2ssa repo.
"""

from svg2ssa.__main__ import cli

cli()
