import re

from .core import SVGContainerEntity
from .attributes.misc import SVGId, SVGStrokeWidth
from .attributes.color import SVGColor, SVGFill, SVGStroke
from .attributes.opacity import SVGOpacity, SVGFillOpacity, SVGStrokeOpacity
from .attributes.transform import SVGTransform, SVGTrafoRotate, SVGTrafoScale
from .attributes.d import SVGD


class SVGElementMixin(SVGContainerEntity):
    """Contains common attributes and methods to model SVG elements."""

    atts_color = {"color", "fill", "stroke"}
    """set[str]: Set of color attrs."""
    atts_opacity = {"opacity", "fill-opacity", "stroke-opacity"}
    """set[str]: Set of opacity attrs."""
    atts_rest = {"stroke-width"}
    """set[str]: Other attrs that can be translated to SSA."""
    atts_style = atts_color | atts_opacity | atts_rest
    """set[str]: Attrs that can be contained by attr ``style``."""
    atts_to_class_mapping = {
        "transform": SVGTransform,
        "color": SVGColor,
        "fill": SVGFill,
        "fill-opacity": SVGFillOpacity,
        "opacity": SVGOpacity,
        "stroke": SVGStroke,
        "stroke-opacity": SVGStrokeOpacity,
        "stroke-width": SVGStrokeWidth,
        "d": SVGD,
        "id": SVGId,
    }
    """dict[str, type]: Maps all attrs, that can be specified in SVG elements, to their classes."""

    @classmethod
    def from_raw_data(cls, data):
        """Instantiates classes to model SVG elements, from mapping of attrs in ``data``."""

        # Filter out unsupported attrs.
        atts = {key: val for key, val in data.items() if key in cls.supported}
        # Unpack properties from ``style`` to the common set of attrs.
        if "style" in atts:
            tokens = re.sub(r"\s+", "", atts["style"])
            tokens = re.findall(r"(?:([^:]+?):([^;]+?)(?:;|;\Z|\Z))", tokens)
            if tokens:
                for key, val in tokens:
                    if key in cls.atts_style:
                        atts[key] = val
            del atts["style"]
        # Process attrs.
        atts = {key: cls.atts_to_class_mapping[key].from_raw_data(val) for key, val in atts.items()}
        return cls(atts)

    # Beware of mutability issues.
    def __add__(self, other):
        curr = self.data
        prev = other.data
        for key in prev:
            if key in curr:
                curr[key] += prev[key]
            else:
                curr[key] = prev[key]
        return self


class SVGElementG(SVGElementMixin):
    supported = {"transform", "style"} | SVGElementMixin.atts_style
    """set[str]: Set of attrs supported by SVG element ``g``."""

    @property
    def dtype(self):
        return "g"


class SVGElementPath(SVGElementMixin):
    supported = {"d", "id", "transform", "style"} | SVGElementMixin.atts_style
    """set[str]: Set of attrs supported by SVG element ``path``."""

    @property
    def dtype(self):
        return "path"

    def ssa_repr(self, ssa_repr_config):
        # Process exceptional cases.
        atts = self.data
        # Process trafos.
        if "transform" in atts:
            trafos = atts["transform"]
            # Create ``\org`` if it is absent so that each next SSA layer automatically layed on top of previous w/o any shifting.
            # ATM only VSFilter behaves like this, maybe libass as well, but not ffdshow subtitles filter.
            # ``\pos`` also will do the trick, but if it's not ``\pos(0,0)``.
            if trafos.contains_obj_with_dtype("rotate"):
                if trafos.contains_obj_with_dtype("translate"):
                    for i, trafo in enumerate(trafos):
                        # If there's empty ``\pos``, then there's no need in it, so remove ``\pos``, -- there's still ``\org`` after all.
                        if trafo.dtype == "translate" and trafo.data[0] == 0 and trafo.data[1] == 0:
                            del trafos.data[i]
                            break
                else:
                    # There's still ``\org``, so everything is OK.
                    pass
            else:
                if trafos.contains_obj_with_dtype("translate"):
                    for i, trafo in enumerate(trafos):
                        # If there's empty ```\pos``, then there's no need in it, so remove ``\pos``, but add ``\org(0,0)`` to maintain collision detection override.
                        if trafo.dtype == "translate" and trafo.data[0] == 0 and trafo.data[1] == 0:
                            del trafos.data[i]
                            atts["transform"] = trafos + SVGTrafoRotate((0, 0, 0))
                            break
                else:
                    # There's no ``\org``, so add it.
                    atts["transform"] = trafos + SVGTrafoRotate((0, 0, 0))
            # Create CTM for path to emulate subpixel precision.
            if trafos.contains_obj_with_dtype("matrix"):
                val = 2 ** (ssa_repr_config["magnification_level"] - 1)
                path_ctm = SVGTrafoScale((val, val)).matrix() + trafos.data[0]
            else:
                val = 2 ** (ssa_repr_config["magnification_level"] - 1)
                path_ctm = SVGTrafoScale((val, val)).matrix()
        else:
            # Create trafos with ``\org(0,0)`` and CTM for path.
            atts["transform"] = SVGTransform([SVGTrafoRotate((0, 0, 0))])
            val = 2 ** (ssa_repr_config["magnification_level"] - 1)
            path_ctm = SVGTrafoScale((val, val)).matrix()
        # Process path.
        atts["d"].ctm = path_ctm
        # Process color.
        # ``fill`` attribute has higher priority over ``color``!
        if "fill" in atts:
            if atts["fill"].data is None:
                atts["fill-opacity"] = SVGFillOpacity(0.0)
                del atts["fill"]
            if "color" in atts:
                del atts["color"]
        if "color" in atts:
            if atts["color"].data is None:
                atts["fill-opacity"] = SVGFillOpacity(0.0)
            else:
                # Fixme: Since I stated that "``fill`` attribute has higher priority over ``color``!" (is that right at all?!), maybe I should've checked first whether ``fill`` exists so that I exidentally wouldn't override it?! Check in custom SVG.
                atts["fill"] = SVGFill(atts["color"].data)
            del atts["color"]
        if "stroke" in atts:
            if atts["stroke"].data is None:
                atts["stroke-width"] = SVGStrokeWidth(0.0)
                del atts["stroke"]
        # Process opacity.
        if "opacity" in atts:
            if "fill-opacity" in atts and "stroke-opacity" in atts:
                atts["fill-opacity"] += atts["opacity"]
                atts["stroke-opacity"] += atts["opacity"]
                del atts["opacity"]
            elif "fill-opacity" in atts:
                atts["fill-opacity"] += atts["opacity"]
                del atts["opacity"]
            elif "stroke-opacity" in atts:
                atts["stroke-opacity"] += atts["opacity"]
                del atts["opacity"]
        # Process ``id``.
        if not "id" in atts:
            atts["id"] = SVGId("")
        return {key: att.ssa_repr(ssa_repr_config) for key, att in atts.items()}
