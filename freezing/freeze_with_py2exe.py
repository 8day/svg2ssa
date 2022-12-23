"""Creates standalone executables for Windows.

Users on other systems like Linux and Mac are likely to have Python installed, so for them it's easier to simply install wheel from PyPI.

To "freeze", simply make sure that :mod:`py2exe` and all other dependencies are installed, then run this script.
"""


from py2exe import freeze
from tomlkit import parse


with open("..\\pyproject.toml", "r+t", encoding="utf-8") as file:
    pyproject = file.read()

VERSION = parse(pyproject)["tool"]["poetry"]["version"]

freeze(
    console=[dict(script=".\\boot_svg2ssa.py", dest_base="svg2ssa", icon_resources=[(0, "..\\logo.ico")])],
    options=dict(
        dist_dir=f"..\\dist\\svg2ssa-{VERSION}",
        packages=["xml.etree.ElementTree", "lxml.etree", "lxml._elementpath", "gzip", "defusedxml.ElementTree"],
    ),
    version_info=dict(version=VERSION),
)
