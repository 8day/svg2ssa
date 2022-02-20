# Trafos use tuple as their container for data for immutability.


from math import radians, sin, cos, tan
from ply.lex import lex
from ply.yacc import yacc
from ..core import SVGBasicEntity, SVGContainerEntity


class SVGTrafoMixin(SVGBasicEntity):
    """Generalized superclass for SVG ``transform`` attribute and its "values"."""

    def __add__(self, other):
        if isinstance(other, type(self)):
            # Doesn't work w/o explicit construction of tuple (:class:`range`` vs :class:`tuple`).
            return self.__class__(tuple(i + j for i, j in zip(self.data, other.data)))
        elif isinstance(other, (SVGTrafoMixin, SVGTransform)):
            return self.matrix() + other.matrix()
        else:
            raise TypeError(f"{self.__class__.__name__}: You have tried to concatenate different types of objects.")


class SVGTrafoMatrix(SVGTrafoMixin):
    """Class for SVG ``matrix`` from ``transform`` attr."""

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
    """Class for SVG ``translate`` from ``transform`` attr."""

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
    """Class for SVG ``rotate`` from ``transform`` attr."""

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
    """Class for SVG ``scale`` from ``transform`` attr."""

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
    """Class for SVG ``skewX`` from ``transform`` attr."""

    @property
    def dtype(self):
        return "skewX"

    def matrix(self):
        skX = tan(self.data[0])
        return SVGTrafoMatrix((1, 0, skX, 1, 0, 0))


class SVGTrafoSkewY(SVGTrafoMixin):
    """Class for SVG ``skewY`` from ``transform`` attr."""

    @property
    def dtype(self):
        return "skewY"

    def matrix(self):
        skY = tan(self.data[0])
        return SVGTrafoMatrix((1, skY, 0, 1, 0, 0))


class S2STransformLex:
    literals = r"()"

    reserved = {
        "matrix": "MATRIX",
        "translate": "TRANSLATE",
        "scale": "SCALE",
        "rotate": "ROTATE",
        "skewX": "SKEWX",
        "skewY": "SKEWY",
    }

    tokens = ("NMB",) + tuple(reserved.values())

    t_ignore_WSP = r"[ \t\n\r]"
    t_ignore_COMMA = r","

    def t_ID(t):
        r"[a-zA-Z]{5,}"
        t.type = reserved.get(t.value)
        # Checks whether found word was one from ``reserved``.
        if not t.type:
            t_error(t)
        return t

    def t_NMB(t):
        """[+-]?(?:(?:(?:[0-9]+)?\.(?:[0-9]+)|(?:[0-9]+)\.)(?:[eE][+-]?(?:[0-9]+))?|(?:[0-9]+)(?:[eE][+-]?(?:[0-9]+)))|[+-]?(?:[0-9]+)"""
        t.value = float(t.value)
        return t

    def t_error(t):
        # Fixme: When ``t.value[0]`` will be the last character in the sequence, ``t.value[1:11]`` may cause errors.
        raise Exception(
            f"The next illegal character were found in 'transformation' attribute: '{t.value[0]}'.\n"
            f"These characters were right after it: {t.value[1:11]}"
        )


class S2STransformYacc:
    """Class for PLY Yacc for processing of ``transform`` attr."""

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

    tokens = S2STransformLex.tokens


# Fixme: In its current form it may have issues with empty ``transform-list`` -- it'll simply crash!
class SVGTransform(SVGContainerEntity):
    """Class for SVG ``transform`` attribute.

    Inherited: [...]
    """

    trafos_all = {"matrix", "skewX", "skewY", "scale", "translate", "rotate"}
    """set[str]: IDs of all possible trafos."""
    trafos_unsupported = {"matrix", "skewX", "skewY"}
    """set[str]: IDs of unsupported trafos."""

    @property
    def dtype(self):
        return "transform"

    def matrix(self):
        """Returns sum of all trafos as a matrix :class:`SVGTrafoMatrix`."""
        data = self.data
        acc = data[0].matrix()
        for i in range(1, len(data)):
            acc += data[i].matrix()
        return acc

    @classmethod
    def from_raw_data(cls, data):
        lexer = lex(module=S2STransformLex)
        lexer.input(data)
        parser = yacc(module=S2STransformYacc(), write_tables=0, debug=False)
        return cls(parser.parse(debug=False, lexer=lexer))

    def collapse_consecutive_objects(self):
        """Collapses sequences of consecutive objects with same value of attr ``dtype`` into one object."""

        list_of_objects = self.data
        l = len(list_of_objects) - 1
        i = 0
        while i < l:
            curr = list_of_objects[i]
            next = list_of_objects[i + 1]
            # Items can be merged, so merge next item into current *and* adjust sequence length to account for merge.
            if curr.dtype == next.dtype:
                list_of_objects[i] += next
                del list_of_objects[i + 1]
                l -= 1
            # Items can't be merged, so move to next item.
            else:
                i += 1

    def collapse_unnecessary_trafos(self, unnecessary_transformations):
        """Finds repeated, nonconsecutive trafos and then collapses everything in-between into the matrix (this is handled by trafos themselves).

        Args:
            unnecessary_transformations (set[str]): Trafos that must be collapsed.
        """

        list_of_trafos = self.data

        trafos_unnecessary = SVGTransform.trafos_all & unnecessary_transformations | SVGTransform.trafos_unsupported
        trafos_all_without_unnecessary = SVGTransform.trafos_all - trafos_unnecessary

        # Create dictionary with trafos indices.
        dictionary = {}
        for i, trafo in enumerate(list_of_trafos):
            if trafo.dtype in dictionary:
                dictionary[trafo.dtype].append(i)
            else:
                dictionary[trafo.dtype] = [i]

        # Find index of the furthest unsupported by SSA trafo.
        # By design, the largest idx should be last (since there was no sorting/shuffle applied), so ``max(dictionary[trafo])`` should be equal to ``dictionary[trafo][-1]``.
        idx_unnec = -1
        for trafo in trafos_unnecessary:
            if trafo in dictionary and dictionary[trafo][-1] > idx_unnec:
                idx_unnec = dictionary[trafo][-1]

        # Find index of the furthest repetitive and nonconsecutive trafo.
        # ``trafos_all_without_unnecessary`` *may* be an empty set, it is completely acceptable.
        idx_repet = -1
        for trafo in trafos_all_without_unnecessary:
            if (
                trafo in dictionary
                and len(dictionary[trafo]) > 1
                and dictionary[trafo][-2] > idx_repet
            ):
                # Implies that indices are in the "right" order, i.e. not shuffled.
                # Inside this function it is always true.
                idx_repet = dictionary[trafo][-2]

        # Merge trafos, if need be.
        if idx_unnec != -1 or idx_repet != -1:
            # ``+1`` for making interval inclusive: [n,m] instead of [n,m).
            idx = (idx_unnec if idx_unnec > idx_repet else idx_repet) + 1
            acc = list_of_trafos[0]
            for i in range(1, idx):
                acc += list_of_trafos[i]
            list_of_trafos[:idx] = [acc]

    def ssa_repr(self, ssa_repr_config):
        self.collapse_consecutive_objects()
        self.collapse_unnecessary_trafos(ssa_repr_config["unnecessary_transformations"])
        return "".join(trafo.ssa_repr(ssa_repr_config) for trafo in self.data)

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
