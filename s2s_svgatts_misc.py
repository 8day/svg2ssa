import s2s_runtime_settings
from s2s_core import SVGAttribute
from s2s_utilities import convert_svglength_to_pixels


class SVGId(SVGAttribute):
    """Class for SVG 'id' attribute.

    Value:        <string>
    Initial:      [...]
    Inherited:    no
    """

    @property
    def dtype(self):
        return "id"

    def preprocess(self, data):
        return data

    def update(self, other):
        tmp = other.__class__()
        tmp.data = other.data
        return tmp

    def convert(self):

        # Commas should be replaced to any random characters.
        # It's neccessary since in SSA they used at a format level.

        return self.data.replace(",", "_")


class SVGStrokeWidth(SVGAttribute):
    """Class for SVG 'stroke-width' attribute.

    Value:        <percentage> | <length> | inherit
    Initial:      1
    Inherited:    yes
    """

    @property
    def dtype(self):
        return "stroke-width"

    def preprocess(self, data):
        return convert_svglength_to_pixels(data)

    def update(self, other):
        tmp = self.__class__()
        tmp.data = self.data
        return tmp

    def convert(self):

        # Note: The way that SSA lays out border differs from that of SVG!
        # Quote from "REC-SVG11-20110816/render.html#PaintingShapesAndText":
        # "A stroke operation is centered on the outline of the object; thus,
        # in effect, half of the paint falls on the interior of the shape and
        # half of the paint falls outside of the shape."

        if s2s_runtime_settings.stroke_preservation == 0:
            return r"\bord{0}".format(self.data)
        else:
            return r"\bord{0}".format(self.data / 2)
