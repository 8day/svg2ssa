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
