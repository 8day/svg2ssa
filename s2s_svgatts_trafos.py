# Note: trafos use tuple as their container for data.


from math import radians, sin, cos, tan
from ply_lex import lex
from ply_yacc import yacc
import ply_lex_transform
from s2s_core import SVGAttribute, S2SBlockContainer, S2STypeError
from s2s_utilities import collapse_consecutive_objects, collapse_unnecessary_trafos


class SVGBlockTrafo(SVGAttribute):
    """Generalised superclass for SVG "transform" attribute and its "values"."""

    def update(self, other):
        if isinstance(other, type(self)):
            tmp = self.__class__()
            # W/o tuple() this doesn't work.
            tmp.data = tuple(i + j for i, j in zip(self.data, other.data))
            return tmp
        elif isinstance(other, SVGBlockTrafo):
            tmp = self.matrix + other.matrix
            return tmp
        else:
            message = ": You have tried to concatenate different types of objects."
            raise S2STypeError(self.__class__.__name__ + message)


class SVGTrafoMatrix(SVGBlockTrafo):
    """Class for SVG "transform" "matrix"."""

    @property
    def dtype(self):
        return "matrix"

    @property
    def matrix(self):
        return self

    def preprocess(self, data):
        return data

    def update(self, other):
        if isinstance(other, SVGTrafoMatrix):
            ctm = self.data
            m = other.data
            data = (
                ctm[0] * m[0] + ctm[2] * m[1],
                ctm[1] * m[0] + ctm[3] * m[1],
                ctm[0] * m[2] + ctm[2] * m[3],
                ctm[1] * m[2] + ctm[3] * m[3],
                ctm[0] * m[4] + ctm[2] * m[5] + ctm[4],
                ctm[1] * m[4] + ctm[3] * m[5] + ctm[5],
            )
            return SVGTrafoMatrix(data)
        elif isinstance(other, SVGBlockTrafo):
            return self + other.matrix
        else:
            message = ": You have tried to concatenate different types of objects."
            raise S2STypeError(self.__class__.__name__ + message)

    def convert(self):
        return ""


class SVGTrafoTranslate(SVGBlockTrafo):
    """Class for SVG "transform" "translate"."""

    @property
    def dtype(self):
        return "translate"

    @property
    def matrix(self):
        tx, ty = self.data
        return SVGTrafoMatrix((1, 0, 0, 1, tx, ty))

    def preprocess(self, data):
        return data if len(data) == 2 else (data[0], 0)

    def convert(self):
        tx, ty = (round(obj) for obj in self.data)
        return r"\pos({0},{1})".format(tx, ty)


class SVGTrafoRotate(SVGBlockTrafo):
    """Class for SVG "transform" "rotate"."""

    @property
    def dtype(self):
        return "rotate"

    @property
    def matrix(self):
        ra, cx, cy = self.data
        if cx == 0 and cy == 0:
            ra = radians(ra)
            m = SVGTrafoMatrix((cos(ra), sin(ra), -sin(ra), cos(ra), 0, 0))
        else:
            mt1 = SVGTrafoTranslate((cx, cy)).matrix
            mr = SVGTrafoRotate((ra, 0, 0)).matrix
            mt2 = SVGTrafoTranslate((-cx, -cy)).matrix
            m = mt1 + mr + mt2
        return m

    def preprocess(self, data):
        return data if len(data) == 3 else (data[0], 0, 0)

    def convert(self):
        ra, cx, cy = (round(obj) for obj in self.data)
        if ra == 0:
            return r"\org({0},{1})".format(cx, cy)
        else:
            return r"\org({0},{1})\frz{2}".format(cx, cy, -ra)


class SVGTrafoScale(SVGBlockTrafo):
    """Class for SVG "transform" "scale"."""

    @property
    def dtype(self):
        return "scale"

    @property
    def matrix(self):
        sx, sy = self.data
        return SVGTrafoMatrix((sx, 0, 0, sy, 0, 0))

    def preprocess(self, data):
        return data if len(data) == 2 else (data[0], data[0])

    def convert(self):
        sx, sy = (round(obj) for obj in self.data)
        return r"\fscx{0}\fscy{1}".format(sx, sy)


class SVGTrafoSkewX(SVGBlockTrafo):
    """Class for SVG "transform" "skewX"."""

    @property
    def dtype(self):
        return "skewX"

    @property
    def matrix(self):
        skX = tan(self.data[0])
        return SVGTrafoMatrix((1, 0, skX, 1, 0, 0))

    def preprocess(self, data):
        return data

    def convert(self):
        return ""


class SVGTrafoSkewY(SVGBlockTrafo):
    """Class for SVG "transform" "skewY"."""

    @property
    def dtype(self):
        return "skewY"

    @property
    def matrix(self):
        skY = tan(self.data[0])
        return SVGTrafoMatrix((1, skY, 0, 1, 0, 0))

    def preprocess(self, data):
        return data

    def convert(self):
        return ""


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
        p[0] = (p[3], p[4], p[5], p[6], p[7], p[8])
        p[0] = SVGTrafoMatrix(p[0])

    def p_translate(self, p):
        """translate : TRANSLATE "(" NMB NMB ")"
        | TRANSLATE "(" NMB ")"
        """
        if len(p) > 5:
            p[0] = (p[3], p[4])
        else:
            p[0] = (p[3],)
        p[0] = SVGTrafoTranslate(p[0])

    def p_rotate(self, p):
        """rotate : ROTATE "(" NMB NMB NMB ")"
        | ROTATE "(" NMB ")"
        """
        if len(p) == 7:
            p[0] = (p[3], p[4], p[5])
        else:
            p[0] = (p[3],)
        p[0] = SVGTrafoRotate(p[0])

    def p_scale(self, p):
        """scale : SCALE "(" NMB NMB ")"
        | SCALE "(" NMB ")"
        """
        if len(p) == 6:
            p[0] = (p[3], p[4])
        else:
            p[0] = (p[3],)
        p[0] = SVGTrafoScale(p[0])

    def p_skewX(self, p):
        """skewX : SKEWX "(" NMB ")" """
        p[0] = (p[3],)
        p[0] = SVGTrafoSkewX(p[0])

    def p_skewY(self, p):
        """skewY : SKEWY "(" NMB ")" """
        p[0] = (p[3],)
        p[0] = SVGTrafoSkewY(p[0])

    def p_error(self, p):
        raise Exception(
            'Some error happened while "yacc" were parsing "transformation" attribute. '
            "Looks like he encountered incorrect sequence of tokens.\n"
            "First ten characters from that sequence: {0}.\n".format(p[0:11])
        )

    tokens = ply_lex_transform.tokens


class SVGTransform(SVGBlockTrafo, S2SBlockContainer):
    """Class for SVG "transform" attribute.

    Inherited: [...]
    """

    # Note: this class in its current form may have issues
    # with empty 'transform-list'. It'll simply crash!

    @property
    def dtype(self):
        return "transform"

    @property
    def matrix(self):
        data = self.data
        if len(data) > 1:
            acc = data[0].matrix
            for trafo in data[1:]:
                acc += trafo.matrix
            return acc
        else:
            return data[0].matrix

    def preprocess(self, data):
        lexer = lex(module=ply_lex_transform)
        lexer.input(data)
        parser = yacc(module=S2STransformYacc(), write_tables=0, debug=False)
        data = parser.parse(debug=False, lexer=lexer)
        data = collapse_consecutive_objects(data)
        data = collapse_unnecessary_trafos(data)
        return data

    def update(self, other):
        if isinstance(other, SVGTransform):
            # Is this the right order?!
            data = self.data + other.data
        elif isinstance(other, SVGBlockTrafo):
            # Same here.
            data = self.data + [other]
        else:
            message = ": You have tried to concatenate different types of objects."
            raise S2STypeError(self.__class__.__name__ + message)
        data = collapse_consecutive_objects(data)
        data = collapse_unnecessary_trafos(data)
        trafos = SVGTransform()
        trafos.data = data
        return trafos

    def convert(self):
        return "".join(trafo.convert() for trafo in self.data)
