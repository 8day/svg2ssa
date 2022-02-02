# Note: trafos use tuple as their container for data.


from math import radians, sin, cos, tan
from ply_lex import lex
from ply_yacc import yacc
import ply_lex_transform
from s2s_core import SVGBasicEntity, SVGContainerEntity
from s2s_utilities import collapse_consecutive_objects, collapse_unnecessary_trafos


class SVGTrafoMixin(SVGBasicEntity):
    """Generalised superclass for SVG "transform" attribute and its "values"."""

    def ssa_repr(self, ssa_repr_config):
        return ""

    def __add__(self, other):
        if isinstance(other, type(self)):
            # W/o tuple() this doesn't work.
            return self.__class__(tuple(i + j for i, j in zip(self.data, other.data)))
        elif isinstance(other, (SVGTrafoMixin, SVGTransform)):
            return self.matrix() + other.matrix()
        else:
            raise TypeError(f"{self.__class__.__name__}: You have tried to concatenate different types of objects.")


class SVGTrafoMatrix(SVGTrafoMixin):
    """Class for SVG "transform" "matrix"."""

    @property
    def dtype(self):
        return "matrix"

    def matrix(self):
        return self

    def __add__(self, other):
        if isinstance(other, SVGTrafoMatrix):
            ctm0, ctm1, ctm2, ctm4, ctm5 = self.data
            m0, m1, m2, m3, m4, m5 = other.data
            data = (
                ctm0 * m0 + ctm2 * m1,
                ctm1 * m0 + ctm3 * m1,
                ctm0 * m2 + ctm2 * m3,
                ctm1 * m2 + ctm3 * m3,
                ctm0 * m4 + ctm2 * m5 + ctm4,
                ctm1 * m4 + ctm3 * m5 + ctm5,
            )
            return SVGTrafoMatrix(data)
        elif isinstance(other, SVGTrafoMixin):
            return self + other.matrix()
        else:
            raise TypeError(f"{self.__class__.__name__}: You have tried to concatenate different types of objects.")


class SVGTrafoTranslate(SVGTrafoMixin):
    """Class for SVG "transform" "translate"."""

    def __init__(self, data):
        super().__init__(data if len(data) == 2 else (data[0], 0))

    @property
    def dtype(self):
        return "translate"

    def matrix(self):
        tx, ty = self.data
        return SVGTrafoMatrix((1, 0, 0, 1, tx, ty))

    def ssa_repr(self, ssa_repr_config):
        tx, ty = (round(obj) for obj in self.data)
        return f"\\pos({tx},{ty})"


class SVGTrafoRotate(SVGTrafoMixin):
    """Class for SVG "transform" "rotate"."""

    def __init__(self, data):
        super().__init__(data if len(data) == 3 else (data[0], 0, 0))

    @property
    def dtype(self):
        return "rotate"

    def matrix(self):
        ra, cx, cy = self.data
        if cx == 0 and cy == 0:
            ra = radians(ra)
            m = SVGTrafoMatrix((cos(ra), sin(ra), -sin(ra), cos(ra), 0, 0))
        else:
            mt1 = SVGTrafoTranslate((cx, cy)).matrix()
            mr = SVGTrafoRotate((ra, 0, 0)).matrix()
            mt2 = SVGTrafoTranslate((-cx, -cy)).matrix()
            m = mt1 + mr + mt2
        return m

    def ssa_repr(self, ssa_repr_config):
        ra, cx, cy = (round(obj) for obj in self.data)
        if ra == 0:
            return f"\\org({cx},{cy})"
        else:
            return f"\\org({cx},{cy})\frz{-ra}"


class SVGTrafoScale(SVGTrafoMixin):
    """Class for SVG "transform" "scale"."""

    def __init__(self, data):
        super().__init__(data if len(data) == 2 else (data[0], data[0]))

    @property
    def dtype(self):
        return "scale"

    def matrix(self):
        sx, sy = self.data
        return SVGTrafoMatrix((sx, 0, 0, sy, 0, 0))

    def ssa_repr(self, ssa_repr_config):
        sx, sy = (round(obj) for obj in self.data)
        return f"\\fscx{sx}\fscy{sy}"


class SVGTrafoSkewX(SVGTrafoMixin):
    """Class for SVG "transform" "skewX"."""

    @property
    def dtype(self):
        return "skewX"

    def matrix(self):
        skX = tan(self.data[0])
        return SVGTrafoMatrix((1, 0, skX, 1, 0, 0))


class SVGTrafoSkewY(SVGTrafoMixin):
    """Class for SVG "transform" "skewY"."""

    @property
    def dtype(self):
        return "skewY"

    def matrix(self):
        skY = tan(self.data[0])
        return SVGTrafoMatrix((1, skY, 0, 1, 0, 0))


class S2STransformYacc:
    """Class for PLY Yacc for trafos."""

    def p_trafos_list(self, p):
        """trafos_list : trafos_list trafo
        | trafo
        """
        p[0] = p[1]
        if len(p) == 3:
            p[0] += p[2]

    def p_trafo(self, p):
        """trafo : matrix
        | translate
        | scale
        | rotate
        | skewX
        | skewY
        """
        p[0] = [p[1]]

    def p_matrix(self, p):
        """matrix : MATRIX "(" NMB NMB NMB NMB NMB NMB ")" """
        p[0] = SVGTrafoMatrix((p[3], p[4], p[5], p[6], p[7], p[8]))

    def p_translate(self, p):
        """translate : TRANSLATE "(" NMB NMB ")"
        | TRANSLATE "(" NMB ")"
        """
        p[0] = SVGTrafoTranslate((p[3], p[4]) if len(p) > 5 else (p[3],))

    def p_rotate(self, p):
        """rotate : ROTATE "(" NMB NMB NMB ")"
        | ROTATE "(" NMB ")"
        """
        p[0] = SVGTrafoRotate((p[3], p[4], p[5]) if len(p) == 7 else (p[3],))

    def p_scale(self, p):
        """scale : SCALE "(" NMB NMB ")"
        | SCALE "(" NMB ")"
        """
        p[0] = SVGTrafoScale((p[3], p[4]) if len(p) == 6 else (p[3],))

    def p_skewX(self, p):
        """skewX : SKEWX "(" NMB ")" """
        p[0] = SVGTrafoSkewX((p[3],))

    def p_skewY(self, p):
        """skewY : SKEWY "(" NMB ")" """
        p[0] = SVGTrafoSkewY((p[3],))

    def p_error(self, p):
        raise Exception(
            "Some error happened while 'yacc' were parsing 'transformation' attribute. "
            "Looks like he encountered incorrect sequence of tokens.\n"
            f"First ten characters from that sequence: {p[0:11]}.\n"
        )

    tokens = ply_lex_transform.tokens


class SVGTransform(SVGContainerEntity):
    """Class for SVG "transform" attribute.

    Inherited: [...]
    """

    # Note: this class in its current form may have issues
    # with empty 'transform-list'. It'll simply crash!

    @property
    def dtype(self):
        return "transform"

    def matrix(self):
        data = self.data
        acc = data[0].matrix()
        for i in range(1, len(data)):
            acc += data[i].matrix()
        return acc

    @classmethod
    def from_raw_data(cls, data):
        lexer = lex(module=ply_lex_transform)
        lexer.input(data)
        parser = yacc(module=S2STransformYacc(), write_tables=0, debug=False)
        return cls(parser.parse(debug=False, lexer=lexer))

    def ssa_repr(self, ssa_repr_config):
        trafos = collapse_consecutive_objects(self.data)
        trafos = collapse_unnecessary_trafos(trafos, ssa_repr_config["unnecessary_transformations"])
        return "".join(trafo.ssa_repr(ssa_repr_config) for trafo in trafos)

    def __add__(self, other):
        if isinstance(other, SVGTransform):
            # Is this the right order?!
            data = self.data + other.data
        elif isinstance(other, SVGTrafoMixin):
            # Same here.
            data = self.data + [other]
        else:
            raise TypeError(f"{self.__class__.__name__}: You have tried to concatenate different types of objects.")
        return SVGTransform(data)
