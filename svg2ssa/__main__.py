"""Logic for use of svg2ssa as a proper standalone app."""


# pylint: disable=import-outside-toplevel
def cli():
    """Reusable CLI logic."""

    from sys import argv as sys_argv
    from os import path as os_path
    from argparse import ArgumentParser

    from .document import SVG

    config = SVG.default_ssa_repr_config

    parser = ArgumentParser(
        description="Converts SVG (Rec 1.1) into SSA (v4.0+).",
    )
    parser.add_argument(
        "-t",
        "--unnecessary_transformations",
        help="Trafos that should be collapsed into matrix, i.e. 'baked'.",
        default=list(config["unnecessary_transformations"]),
        choices=["scale", "translate", "rotate"],
        nargs="*",
    )
    parser.add_argument(
        "-m",
        "--magnification_level",
        help="Magnification level of the coordinate system by this formula: (level - 1) ^ 2.",
        default=config["magnification_level"],
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
        default=config["stroke_preservation"],
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
        default=config["width"],
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
        default=config["height"],
        type=int,
        metavar="int",
    )
    parser.add_argument(
        "-i",
        "--file_in",
        help="SVG file to be read. Path containing whitespace must be quoted.",
        default="",
        metavar="str",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--file_out",
        help="SSA file to be written. Path containing whitespace must be quoted.",
        default="",
        metavar="str",
    )

    args = vars(parser.parse_args(sys_argv[1:]))
    args["unnecessary_transformations"] = set(args["unnecessary_transformations"])

    file_in = args.pop("file_in")
    file_out = args.pop("file_out")

    if os_path.isfile(file_in):
        svg = SVG()
        svg.from_svg_file(file_in)
        # User shouldn't be able to inject anything bad because :mod:`argparse` checks whether option is supported, so this should be safe.
        # :mod:`argparse` maps data to ``--``-prefixed options instead of ``-``-prefixed, therefore this will result in something like ``stroke_preservation = 1`` and not ``s = 1`` or whatever.
        svg.to_ssa_file(file_out if file_out else f"{file_in}.ass", args)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
