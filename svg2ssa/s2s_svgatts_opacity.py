# Seems that a real problem is that not all properties are inherited from ``g``-elements etc. E.g., ``stroke-opacity`` with the same value on ``path``-element and ``g``-element doesn't have 1/2 effect, it stayed the same in IE browser. Seems that only ``opacity`` affects subsequent elements and ``stroke-opacity``, ``fill-opacity`` etc. override the same properties on g-element/containers.

# Fixme: ``fill-opacity`` & ``opacity`` conflict: ``fill-opacity`` should depend on ``opacity``! I.e. when ``opacity=.5`` and ``fill-opacity=.5``, opacity in SSA must be .25, not .5!

# Todo: Since all opacity classes mostly differ by SSA representation string, it'd be probably better to add some code to replace the string to class corresponding one. I.e. ``r"\alpha&H{0:02X}&"`` replaced to ``r"\1a&H{0:02X}&"`` if class is :class:`SVGFillOpacity`. Though it may be a bad idea, since the same thing can be done to color, but there this modification will be overwhelming, unnecessary. So, it's probably better to leave it as is. Well, as I said, ATM this kind of optimization is unnecessary.


from s2s_core import SVGBasicEntity


class SVGOpacity(SVGBasicEntity):
    """Class for SVG ``opacity`` attribute.

    Value:        <opacity-value> | inherit
    Initial:      1
    Inherited:    no
    """

    @property
    def dtype(self):
        return "opacity"

    # Todo: Add clamping of out-of-range values.
    @classmethod
    def from_raw_data(cls, data):
        return cls(float(data))

    def ssa_repr(self, ssa_repr_config):
        return f"\\alpha&H{round(255 - (self.data * 255)):02X}&"

    def __add__(self, other):
        # Creation of the third object is necessary since w/o it ``self`` or ``other`` may (and will) be modified later on, which is wrong.
        return self.__class__(self.data * other.data)


class SVGFillOpacity(SVGOpacity):
    """Class for SVG ``fill-opacity`` attribute.

    Value:        <opacity-value> | inherit
    Initial:      1
    Inherited:    yes
    """

    @property
    def dtype(self):
        return "fill-opacity"

    def ssa_repr(self, ssa_repr_config):
        return f"\\1a&H{round(255 - (self.data * 255)):02X}&"


class SVGStrokeOpacity(SVGOpacity):
    """Class for SVG ``stroke-opacity`` attribute.

    Value:        <opacity-value> | inherit
    Initial:      1
    Inherited:    yes
    """

    @property
    def dtype(self):
        return "stroke-opacity"

    def ssa_repr(self, ssa_repr_config):
        return f"\\3a&H{round(255 - (self.data * 255)):02X}&"
