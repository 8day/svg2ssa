import s2s_runtime_settings
from s2s_core import SVGBasicEntity
from s2s_utilities import convert_svglength_to_pixels


class SVGId(SVGBasicEntity):
    """Class for SVG 'id' attribute.

    Value:        <string>
    Initial:      [...]
    Inherited:    no
    """

    @property
    def dtype(self):
        return "id"

    @classmethod
    def from_raw_data(cls, data):
        return cls(data)

    def __add__(self, other):
        return other.__class__(other.data)

    def ssa_repr(self):

        # Commas should be replaced to any random characters.
        # It's neccessary since in SSA they used at a format level.

        return self.data.replace(",", "_")


class SVGStrokeWidth(SVGBasicEntity):
    """Class for SVG 'stroke-width' attribute.

    Value:        <percentage> | <length> | inherit
    Initial:      1
    Inherited:    yes
    """

    @property
    def dtype(self):
        return "stroke-width"

    @classmethod
    def from_raw_data(cls, data):
        return cls(convert_svglength_to_pixels(data))

    def __add__(self, other):
        return self.__class__(self.data)

    def ssa_repr(self):

        # Note: The way that SSA lays out border differs from that of SVG!
        # Quote from "REC-SVG11-20110816/render.html#PaintingShapesAndText":
        # "A stroke operation is centered on the outline of the object; thus,
        # in effect, half of the paint falls on the interior of the shape and
        # half of the paint falls outside of the shape."

        stroke = s2s_runtime_settings.stroke_preservation
        if stroke == 0:
            return r"\bord{0}".format(self.data)
        elif stroke == 1:
            return r"\bord{0}".format(self.data / 2)
        else:
            raise ValueError("Unknown value for 's2s_runtime_settings.stroke_preservation': {0!s}".format(stroke))
