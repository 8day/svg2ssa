"""Logic for use of svg2ssa as a proper standalone app."""


from sys import argv as sys_argv
from os import path as os_path
from argparse import ArgumentParser
from importlib import import_module

from .document import SVG

config = SVG.default_ssa_repr_config


# pylint: disable=import-outside-toplevel
def cli(
    t=list(config["unnecessary_transformations"]),
    m=config["magnification_level"],
    s=config["stroke_preservation"],
    x=config["width"],
    y=config["height"],
    i="",
    o="",
    p="defusedxml.ElementTree",
):
    """Reusable CLI logic."""

    parser = ArgumentParser(
        description="Converts SVG (Rec 1.1) into SSA (v4.0+).",
    )
    parser.add_argument(
        "-t",
        "--unnecessary_transformations",
        help="Trafos that should be collapsed into matrix, i.e. 'baked'.",
        default=t,
        choices=["scale", "translate", "rotate"],
        nargs="*",
    )
    parser.add_argument(
        "-m",
        "--magnification_level",
        help="Magnification level of the coordinate system by this formula: (level - 1) ^ 2.",
        default=m,
        type=int,
        metavar="int",
    )
    parser.add_argument(
        "-s",
        "--stroke_preservation",
        help=(
            "Stroke transformation. '0' preserves stroke width (left untouched); "
            "'1' preserve stroke area (stroke size is divided by 2)."
        ),
        default=s,
        type=int,
        choices=range(2),
    )
    parser.add_argument(
        "-x",
        "--default_playresx",
        help=(
            "Default PlayResX for SSA script in case if SVG counterpart won't be set. "
            "Should be equal to the video dimensions (and/or to the drawing being converted). "
            "Checked for mod16."
        ),
        default=x,
        type=int,
        metavar="int",
    )
    parser.add_argument(
        "-y",
        "--default_playresy",
        help=(
            "Default PlayResY for SSA script in case if SVG counterpart won't be set. "
            "Should be equal to the video dimensions (and/or to the drawing being converted). "
            "Checked for mod16."
        ),
        default=y,
        type=int,
        metavar="int",
    )
    parser.add_argument(
        "-i",
        "--file_in",
        help="SVG file to be read. Path containing whitespace must be quoted.",
        default=i,
        metavar="str",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--file_out",
        help="SSA file to be written. Path containing whitespace must be quoted.",
        default=o,
        metavar="str",
    )
    parser.add_argument(
        "-p",
        "--xml_parser",
        help="Name of an XML parser object with an API equivalent to xml.etree.ElementTree.",
        default=p,
        # Because of dynamic importing with :func:`importlib.import_module`, for safety set of available parsers must be limited to known parsers.
        choices=["defusedxml.ElementTree", "lxml.etree", "xml.etree.ElementTree"],
    )

    args = vars(parser.parse_args(sys_argv[1:]))
    args["unnecessary_transformations"] = set(args["unnecessary_transformations"])

    file_in = args.pop("file_in")
    file_out = args.pop("file_out")
    xml_parser = import_module(args.pop("xml_parser"))

    if os_path.isfile(file_in):
        svg = SVG()
        svg.from_svg_file(file_in, xml_parser)
        # User shouldn't be able to inject anything bad because :mod:`argparse` checks whether option is supported, so this should be safe.
        # :mod:`argparse` maps data to ``--``-prefixed options instead of ``-``-prefixed, therefore this will result in something like ``stroke_preservation = 1`` and not ``s = 1`` or whatever.
        svg.to_ssa_file(file_out if file_out else f"{file_in}.ass", args)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
