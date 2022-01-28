import re

# Uncomment when cx_Freeze'ing with lxml.
# from lxml import etree

# Uncomment when cx_Freeze'ing with xml.etree.
# from xml.etree import ElementTree as etree

# Comment when cx_Freeze'ing to prevent loading of lxml even if xml.etree is needed.
try:
    from lxml import etree
except ImportError:
    # See: http://lxml.de/compatibility.html
    from xml.etree import ElementTree as etree

import s2s_runtime_settings
from s2s_elems import SVGElement
from s2s_utilities import convert_svglength_to_pixels


class S2S:
    """This is 'main()', if you like. Spins all the machinery behind it."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.element_stack = []
        self.container_stack = []
        self.ssa_meta = {}

    @staticmethod
    def make_round_and_mod(nmb, mod):
        nmb = round(nmb)
        if nmb % mod != 0:
            nmb += mod - (nmb % mod)
        return nmb

    def start_event_for_g(self, atts):
        curr = SVGElement.from_raw_data("g", atts)
        try:
            prev = self.container_stack[-1]
            curr += prev
        except IndexError:
            pass
        self.container_stack.append(curr)

    def end_event_for_g(self):
        if self.container_stack:
            del self.container_stack[-1]

    def start_event_for_path(self, atts):
        curr = SVGElement.from_raw_data("path", atts)
        try:
            prev = self.container_stack[-1]
            curr += prev
        except IndexError:
            pass
        self.element_stack.append(curr)

    def end_event_for_path(self):
        pass

    def start_event_for_svg(self, atts):
        width = atts.get("width")
        height = atts.get("height")
        if width is not None and height is not None:
            width = atts["width"]
            height = atts["height"]
            width = convert_svglength_to_pixels(width)
            height = convert_svglength_to_pixels(height)
            width = S2S.make_round_and_mod(width, 16)
            height = S2S.make_round_and_mod(height, 16)
        else:
            width = s2s_runtime_settings.ssa_default_playresx
            height = s2s_runtime_settings.ssa_default_playresx
        self.ssa_meta["playresx"] = width
        self.ssa_meta["playresy"] = height

    def end_event_for_svg(self):
        pass

    start = dict(
        path=start_event_for_path, g=start_event_for_g, svg=start_event_for_svg
    )

    end = dict(path=end_event_for_path, g=end_event_for_g, svg=end_event_for_svg)

    def ssa_repr(self):
        filepath = self.filepath
        for action, element in etree.iterparse(filepath, ("start", "end")):
            ns_name, local_name = re.search(r"^(\{.+?\})(.+)$", element.tag).group(1, 2)
            if action == "start":
                if local_name in S2S.start:
                    S2S.start[local_name](self, element.attrib)
            else:
                if local_name in S2S.end:
                    S2S.end[local_name](self)

        ssa_table = []
        for element in self.element_stack:
            atts = element.ssa_repr()
            ssa_table.append(
                s2s_runtime_settings.ssa_event.format(
                    actor=atts.pop("id"),
                    trans=atts.pop("transform"),
                    drwng=atts.pop("d"),
                    m_lev=s2s_runtime_settings.magnification_level,
                    codes="".join(obj for key, obj in atts.items()),
                )
            )
        ssa_table = "\n".join(ssa_table)

        ssa_header = s2s_runtime_settings.ssa_header.format(
            width=self.ssa_meta["playresx"], height=self.ssa_meta["playresy"]
        )
        with open(filepath + ".ass", "w+t", buffering=65536) as fh:
            fh.write(ssa_header)
            fh.write("\n")
            fh.write(ssa_table)
            fh.write("\n")
            print(
                "Successfully converted:",
                filepath if len(filepath) < 52 else "..." + filepath[-52:],
            )

        self.element_stack = []
        self.container_stack = []
        self.ssa_meta = {}


if __name__ == "__main__":
    from sys import argv as sys_argv
    from os import path as os_path
    from argparse import ArgumentParser, REMAINDER

    parser = ArgumentParser(
        description="Converts SVG (Rec 1.1) into SSA (v4.0+).",
        epilog='To run, use this syntax: APP_NAME KEYS PATH_TO_THE_FILE. Beware that 1) there\'s no key to specify output file (this file will be automatically placed inside same dir as SVG, with the same name as SVG, but with suffix ".ass"); 2) only one file can be converted at a time, do not specify multiple files.',
    )
    parser.add_argument(
        "-t",
        "--unnecessary_transformations",
        help='Trafos that should be collapsed into matrix, i.e. "baked". If N trafos are used, then the key should be used N times: -t rotate -t skewX.',
        default=[],
        action="append",
        choices=["scale", "translate", "rotate"],
    )
    parser.add_argument(
        "-m",
        "--magnification_level",
        help="Magnification level of the coordinate system by this formula: (level - 1) ^ 2.",
        default=3,
        type=int,
        metavar="natural_number",
    )
    parser.add_argument(
        "-s",
        "--stroke_preservation",
        help='Stroke transformation. "0" preserves stroke width (left untouched); "1" preserve stroke area (stroke size is divided by 2).',
        default=0,
        type=int,
        choices=range(2),
    )
    parser.add_argument(
        "-c",
        "--collapse_consecutive_path_segments",
        help="Collapses consecutive path segments of the same type into one: l 10,10 l 20,20 >>> l 10,10 20,20.",
        default=1,
        type=int,
        choices=range(2),
    )
    parser.add_argument(
        "-x",
        "--ssa_default_playresx",
        help="Custom PlayResX for SSA script. Should be equal to the video dimensions (and/or to the drawing being converted). When custom PlayResX is set, mod16 is checked.",
        default=1280,
        type=int,
        metavar="natural_number",
    )
    parser.add_argument(
        "-y",
        "--ssa_default_playresy",
        help="Custom PlayResY for SSA script. Should be equal to the video dimensions (and/or to the drawing being converted). When custom PlayResY is set, mod16 is checked.",
        default=720,
        type=int,
        metavar="natural_number",
    )
    parser.add_argument("path", nargs=REMAINDER)

    args = vars(parser.parse_args(sys_argv[1:]))

    # Pop positional path argument and join path segments split at whitespace.
    path = " ".join(args.pop("path"))

    # User shouldn't be able to inject anything bad because :mod:`argparse` checks whether option is supported, so this should be safe.
    # :mod:`argparse` maps data to ``--``-prefixed options instead of ``-``-prefixed, therefore this will result in something like ``s2s_runtime_settings.stroke_preservation = 1`` and not ``s2s_runtime_settings.s = 1`` or whatever.
    for k, v in args.items():
        setattr(s2s_runtime_settings, k, v)

    s2s_runtime_settings.ssa_header = (
        "[Script Info]\n"
        "; Script generated by svg2ssa for use in Aegisub\n"
        "; svg2ssa: *somewhere-in-Internet*\n"
        "; Aegisub: http://www.aegisub.org/\n"
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
    )
    s2s_runtime_settings.ssa_event = "Dialogue: 0,0:00:00.00,0:00:02.00,s2s.default,{actor},0000,0000,0000,,{{\\p{m_lev}{trans}{codes}}} {drwng} {{\\p0}}"

    if os_path.isfile(path):
        S2S(path).ssa_repr()
    else:
        parser.print_help()
