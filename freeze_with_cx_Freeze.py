"""Creates standalone executables for Windows.

Users on other systems like Linux and Mac are likely to have Python installed, so for them it's easier to simply install wheel from PyPI.

To "freeze", simply make sure that :mod:`cx_Freeze` and all other dependencies are installed, then run this script.
"""


from shutil import make_archive, rmtree 

from cx_Freeze.executable import Executable
from cx_Freeze.freezer import Freezer
from tomlkit import parse


with open("..\\pyproject.toml", "r+t", encoding="utf-8") as file:
    pyproject = file.read()

VERSION = parse(pyproject)["tool"]["poetry"]["version"]

freezer = Freezer(
    [Executable(".\\boot_svg2ssa.py", target_name="svg2ssa", icon="..\\logo.ico")],
    packages=["xml.etree.ElementTree", "lxml.etree", "lxml._elementpath", "gzip", "defusedxml.ElementTree"],
    targetDir=f"..\\dist\\svg2ssa-{VERSION}",
)
freezer.Freeze()

make_archive(f"..\\dist\\svg2ssa-{VERSION}", "zip", "..\\dist", f".\\svg2ssa-{VERSION}")
rmtree(f"..\\dist\\svg2ssa-{VERSION}")
