import re

# Uncomment when cx_Freeze'ing with :mod:`lxml`.
# from lxml import etree

# Uncomment when cx_Freeze'ing with :mod:`xml.etree`.
# from xml.etree import ElementTree as etree

# Comment when cx_Freeze'ing to prevent loading of :mod:`lxml` even if :mod:`xml.etree` is needed.
try:
    from lxml import etree
except ImportError:
    # See http://lxml.de/compatibility.html.
    from xml.etree import ElementTree as etree

from .s2s_elems import SVGElementG, SVGElementPath
from .utilities import convert_svglength_to_pixels


DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1088


class SVG:
    """Models Scalable Vector Graphics document convertable to SubStation Alpha subtitle document."""

    def __init__(self):
        self.terminal_element_stack = []
        """list: Sequence with terminal elements convertable to SSA."""
        self.container_element_stack = []
        """list: Sequence with container elements whose attrs must be passed to enclosed terminal elements."""
        self.width = DEFAULT_WIDTH
        """int: Default width for the generated SSA document."""
        self.height = DEFAULT_HEIGHT
        """int: Default height for the generated SSA document."""
        self.default_ssa_repr_config = dict(
            unnecessary_transformations=set(),
            stroke_preservation=0,
            magnification_level=3,
            default_playresx=DEFAULT_WIDTH,
            default_playresy=DEFAULT_HEIGHT,
            header_template = (
                "[Script Info]\n"
                "; Script generated by svg2ssa for use in Aegisub\n"
                "; svg2ssa: https://github.com/8day/svg2ssa\n"
                "; Aegisub: https://github.com/Aegisub/Aegisub\n"
                "ScriptType: v4.00+\n"
                "Title: SSA subtitle generated from SVG\n"
                "WrapStyle: 0\n"
                "PlayResX: {width}\n"
                "PlayResY: {height}\n"
                "ScaledBorderAndShadow: yes\n"
                "Video File: ?dummy:23.976000:100000:{width}:{height}:255:255:255:\n"
                "\n"
                "[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
                "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
                "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                "Alignment, MarginL, MarginR, MarginV, Encoding\n"
                "Style: s2s.default,Arial,20,"
                "&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
                "0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1\n"
                "\n"
                "[Events]\n"
                "Format: Layer, Start, End, Style, Name, "
                "MarginL, MarginR, MarginV, Effect, Text"
            ),
            event_template = (
                "Dialogue: 0,0:00:00.00,0:00:02.00,s2s.default,{actor},0000,0000,0000,,"
                "{{\\p{m_lev}{trans}{codes}}} {drwng} {{\\p0}}"
            ),
        )
        """dict: Template config for conversion to SSA."""

    @staticmethod
    def make_round_and_mod(nmb, mod):
        """Returns ``nmb`` suitable for use as the size of a side of a video frame.

        Args:
            nmb (int): Size of one of the sides of a picture.
            mod (int): Modulus.
        Returns:
            int: Rounded ``nmb``.
        """
        nmb = round(nmb)
        if nmb % mod != 0:
            nmb += mod - (nmb % mod)
        return nmb

    def _g_started(self, atts):
        """Builds model of SVG ``g`` element out of its attrs and adds it to :attr:`container_element_stack`. Also merges attrs from parent elements.

        Args:
            atts (dict[str, str]): Attributes of an element.
        """
        curr = SVGElementG.from_raw_data(atts)
        try:
            prev = self.container_element_stack[-1]
            curr += prev
        except IndexError:
            pass
        self.container_element_stack.append(curr)

    def _g_ended(self):
        """Pops built model of SVG ``g`` element from :attr:`container_element_stack`."""
        if self.container_element_stack:
            del self.container_element_stack[-1]

    def _path_started(self, atts):
        """Builds model of SVG ``path`` element out of its attrs and adds it to :attr:`terminal_element_stack`. Also merges attrs from parent elements.

        Args:
            atts (dict[str, str]): Attributes of an element.
        """
        curr = SVGElementPath.from_raw_data(atts)
        try:
            prev = self.container_element_stack[-1]
            curr += prev
        except IndexError:
            pass
        self.terminal_element_stack.append(curr)

    def _path_ended(self):
        """No processing is required for end tag of element ``path``."""
        pass

    def _svg_started(self, atts):
        """Stores SVG :attr:`width` and :attr:`height`.

        Args:
            atts (dict[str, str]): Attributes of an element.
        """
        self.width = atts.get("width")
        self.height = atts.get("height")

    def _svg_ended(self):
        """No processing is required for end tag of element ``svg``."""
        pass

    _start = dict(path=_path_started, g=_g_started, svg=_svg_started)
    """dict[str, Callable[None, [dict, dict]]]: Maps names of elements to handlers of their start tag."""

    _end = dict(path=_path_ended, g=_g_ended, svg=_svg_ended)
    """dict[str, Callable[None, [dict, dict]]]: Maps names of elements to handlers of their end tag."""

    def from_svg_file(self, filepath):
        """Constructs :class:`SVG` out of SVG file stored under ``filepath``.

        Args:
            filepath (str): Path to SVG file to be read.
        """
        for action, element in etree.iterparse(filepath, ("start", "end")):
            ns_name, local_name = re.search(r"^(\{.+?\})(.+)$", element.tag).group(1, 2)
            if action == "start":
                if local_name in SVG._start:
                    SVG._start[local_name](self, element.attrib)
            else:
                if local_name in SVG._end:
                    SVG._end[local_name](self)

    def to_ssa_file(self, filepath, ssa_repr_config):
        """Converts :class:`SVG` to its SSA representation using ``ssa_repr_config``, then saves it under ``filepath``.

        Args:
            filepath (str): Path to SSA file to be written.
            ssa_repr_config (dict): See :attr:`SVG.default_ssa_repr_config`.
        """
        ssa = self.ssa_repr({**self.default_ssa_repr_config, **ssa_repr_config})
        with open(filepath, "w+t", buffering=65536, encoding="utf-8") as fh:
            fh.write(ssa)
            fh.write("\n")

    def ssa_repr(self, ssa_repr_config):
        """Creates SSA representation from an instance of :class:`SVG`.

        Args:
            ssa_repr_config (dict): See :attr:`SVG.default_ssa_repr_config`.
        Returns:
            str: Contents of SSA document.
        """
        ssa = []

        if self.width is not None and self.height is not None:
            width = convert_svglength_to_pixels(self.width)
            height = convert_svglength_to_pixels(self.height)
            width = SVG.make_round_and_mod(width, 16)
            height = SVG.make_round_and_mod(height, 16)
        else:
            width = ssa_repr_config["default_playresx"]
            height = ssa_repr_config["default_playresx"]
        ssa.append(ssa_repr_config["header_template"].format(width=width, height=height))

        for element in self.terminal_element_stack:
            atts = element.ssa_repr(ssa_repr_config)
            ssa.append(ssa_repr_config["event_template"].format(
                actor=atts.pop("id"),
                trans=atts.pop("transform"),
                drwng=atts.pop("d"),
                m_lev=ssa_repr_config["magnification_level"],
                codes="".join(atts.values()),
            ))

        return "\n".join(ssa)


if __name__ == "__main__":
    from sys import argv as sys_argv
    from os import path as os_path
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="Converts SVG (Rec 1.1) into SSA (v4.0+).",
    )
    parser.add_argument(
        "-t",
        "--unnecessary_transformations",
        help="Trafos that should be collapsed into matrix, i.e. 'baked'.",
        default=[],
        choices=["scale", "translate", "rotate"],
        nargs="*",
    )
    parser.add_argument(
        "-m",
        "--magnification_level",
        help="Magnification level of the coordinate system by this formula: (level - 1) ^ 2.",
        default=3,
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
        default=0,
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
        default=DEFAULT_WIDTH,
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
        default=DEFAULT_HEIGHT,
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