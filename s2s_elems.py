from s2s_core import SVGContainerEntity
from s2s_svgatts_misc import SVGId, SVGStrokeWidth
from s2s_svgatts_color import SVGColor, SVGFill, SVGStroke
from s2s_svgatts_opacity import SVGOpacity, SVGFillOpacity, SVGStrokeOpacity
from s2s_svgatts_trafos import SVGTransform, SVGTrafoRotate, SVGTrafoScale
from s2s_svgatts_path import SVGD


class SVGElement(SVGContainerEntity):
    """Converts all the attributes that other classes feed him.

    Currently works only with "path" and "g".
    """

    atts_color = {"color", "fill", "stroke"}
    atts_opacity = {"opacity", "fill-opacity", "stroke-opacity"}
    atts_rest = {"stroke-width"}
    atts_style = atts_color | atts_opacity | atts_rest
    atts_path = {"d", "id", "transform", "style"} | atts_style
    atts_group = {"transform", "style"} | atts_style
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

    def __init__(self, dtype, data):
        self._dtype = dtype
        super().__init__(data)

    @property
    def dtype(self):
        return self._dtype

    @classmethod
    def from_raw_data(cls, dtype, data):
        # Select appropriate set of attributes.
        if dtype == "path":
            supported = cls.atts_path
        elif dtype == "g":
            supported = cls.atts_group
        else:
            raise ValueError(f"Unknown dtype supplied to SVGElement.from_string(): {dtype}.")
        # Filter out unsupported attributes.
        atts = {key: val for key, val in data.items() if key in supported}
        # Unpack properties from "style" to the common set of attributes.
        if "style" in atts:
            tokens = re.sub("\s+", "", atts["style"])
            tokens = re.findall(r"(?:([^:]+?):([^;]+?)(?:;|;\Z|\Z))", tokens)
            if tokens:
                for key, val in tokens:
                    if key in cls.atts_style:
                        atts[key] = val
            del atts["style"]
        # Process attributes.
        atts = {
            key: cls.atts_to_class_mapping[key].from_raw_data(val) for key, val in atts.items()
        }
        return cls(dtype, atts)

    def ssa_repr(self, ssa_repr_config):
        # Process exceptional cases.
        atts = self.data
        # Process trafos.
        if "transform" in atts:
            trafos = atts["transform"]
            # Create \org if it is absent so that each next SSA layer
            # automatically layed on top of previous w/o any shifting.
            # ATM only VSFilter behaves like this, maybe libass as well,
            # but not ffdshow subtitles filter.
            # \pos also will do the trick, but if it's not \pos(0,0).
            if "rotate" in trafos:
                if "translate" in trafos:
                    for i in range(len(trafos)):
                        # If there's empty \pos, then there's no need in it, so remove \pos, -- there's still \org after all.
                        if trafos.data[i].dtype == "translate" and (
                            trafos.data[i].data[0] == 0 and trafos.data[i].data[1] == 0
                        ):
                            del trafos.data[i]
                            break
                else:
                    # There's still \org, so everything is OK.
                    pass
            else:
                if "translate" in trafos:
                    for i in range(len(trafos)):
                        # If there's empty \pos, then there's no need in it, so remove \pos, but add \org(0,0) to maintain collision detection override.
                        if trafos.data[i].dtype == "translate" and (
                            trafos.data[i].data[0] == 0 and trafos.data[i].data[1] == 0
                        ):
                            del trafos.data[i]
                            atts["transform"] = trafos + SVGTrafoRotate((0, 0, 0))
                            break
                else:
                    # There's no \org, so add it.
                    atts["transform"] = trafos + SVGTrafoRotate((0, 0, 0))
            # Create CTM for path to emulate subpixel precision.
            if "matrix" in trafos:
                val = 2 ** (ssa_repr_config["magnification_level"] - 1)
                path_ctm = SVGTrafoScale((val, val)).matrix + trafos.data[0]
            else:
                val = 2 ** (ssa_repr_config["magnification_level"] - 1)
                path_ctm = SVGTrafoScale((val, val)).matrix
        else:
            # Create trafos with \org(0,0) and CTM for path.
            atts["transform"] = SVGTransform([SVGTrafoRotate((0, 0, 0))])
            val = 2 ** (ssa_repr_config["magnification_level"] - 1)
            path_ctm = SVGTrafoScale((val, val)).matrix
        # Process path.
        atts["d"].ctm = path_ctm
        # Process color. 'Fill' attribute has higher priority over 'color'!
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
                # Fixme: since I stated that "'Fill' attribute has higher priority over 'color'!!!" (is that right at all?!),
                # maybe I should've checked first whether 'fill' exists so that I exidentally wouldn't override it?!
                # Todo: check in custom SVG.
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
        # Process 'id'.
        if not "id" in atts:
            atts["id"] = SVGId("")
        return {key: att.ssa_repr(ssa_repr_config) for key, att in atts.items()}

    def __add__(self, other):
        # Note: beware of mutability issues.
        curr = self.data
        prev = other.data
        for key in prev:
            curr[key] = curr[key] + prev[key] if key in curr else prev[key]
        return self
