from copy import deepcopy
from math import sqrt
from ply_lex import lex
from ply_yacc import yacc
import ply_lex_d
from s2s_core import SVGBasicEntity, SVGContainerEntity
from s2s_utilities import collapse_consecutive_objects
from s2s_svgatts_trafos import SVGTrafoScale


class SVGDSeg(SVGBasicEntity):
    """Common class for all subpaths used in SVG 'd' attribute.

    Inherited: no
    """

    # Note: separate classes for all commands have not been made because they are
    # useless out of SVGD context. I simply cannot properly convert them w/o knowing
    # current point of previous segment.

    ssa_comm_type = dict(M="m", L="l", C="b")

    def __init__(self, dtype, data):
        self._dtype = dtype
        super().__init__(data)

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, dtype):
        self._dtype = dtype

    def ssa_repr(self, ssa_repr_config):
        tmp = " ".join(str(round(coord)) for coord in self.data)
        return f"{SVGDSeg.ssa_comm_type[self.dtype]} {tmp}"

    def __add__(self, other):
        return self.__class__(self.dtype, self.data + other.data)


class S2SDYacc:
    """Class for PLY Yacc for "d"."""

    # Note: currently support of some intructions disabled on the Lexer level.
    # BTW, there is a difference in SVG whether 'Z' is present or not: stroke
    # joins are  rendered differently. With SSA that is not the case, so I forced
    # Lexer to ingore 'Z's. In SVG Rec. it's stated: "If you instead "manually"
    # close the subpath via a "lineto" command, the start of the first segment
    # and the end of the last segment are not joined but instead are each capped
    # using the current value of ``stroke-linecap``. At the end of the command,
    # the new current point is set to the initial point of the current subpath."

    mvto_lnto_mapping = {"M": ("M", "L"), "m": ("m", "l")}

    def p_groups_1(self, p):
        """svg_path : m_drawto_grps"""
        p[0] = p[1]

    def p_groups_2(self, p):
        """m_drawto_grps : m_drawto_grps m_drawto_grp
                      | m_drawto_grp
        m_drawto_grp  : m_comm drawto_comms
                      | m_comm
        drawto_comms  : drawto_comms drawto_comm
                      | drawto_comm
        """
        p[0] = p[1]
        if len(p) == 3:
            p[0] = p[0] + p[2]

    def p_groups_3(self, p):
        """drawto_comm : l_comm
        | h_comm
        | v_comm
        | c_comm
        | s_comm
        | q_comm
        | t_comm
        | a_comm
        """
        p[0] = p[1]

    def p_comms_1(self, p):
        """h_comm : "H" h_comm_arg_seq
               | "h" h_comm_arg_seq
        v_comm : "V" v_comm_arg_seq
               | "v" v_comm_arg_seq
        l_comm : "L" l_comm_arg_seq
               | "l" l_comm_arg_seq
        c_comm : "C" c_comm_arg_seq
               | "c" c_comm_arg_seq
        s_comm : "S" s_comm_arg_seq
               | "s" s_comm_arg_seq
        q_comm : "Q" q_comm_arg_seq
               | "q" q_comm_arg_seq
        t_comm : "T" t_comm_arg_seq
               | "t" t_comm_arg_seq
        a_comm : "A" a_comm_arg_seq
               | "a" a_comm_arg_seq
        """
        comm = p[1]
        p[0] = [SVGDSeg(comm, arg_seq) for arg_seq in p[2]]

    def p_comms_2(self, p):
        """m_comm : "M" m_comm_arg_seq
        | "m" m_comm_arg_seq
        """
        mvto, lnto = S2SDYacc.mvto_lnto_mapping[p[1]]
        arg_seqs = p[2]
        segs = [SVGDSeg(mvto, arg_seqs.pop(0))]
        if len(arg_seqs) > 0:
            for arg_seq in arg_seqs:
                segs.append(SVGDSeg(lnto, arg_seq))
        p[0] = segs

    def p_arg_seq_1(self, p):
        """m_comm_arg_seq : m_comm_arg_seq NMB NMB
                       | NMB NMB
        l_comm_arg_seq : l_comm_arg_seq NMB NMB
                       | NMB NMB
        t_comm_arg_seq : t_comm_arg_seq NMB NMB
                       | NMB NMB
        """
        if len(p) == 3:
            p[0] = [[p[1], p[2]]]
        else:
            p[1].append([p[2], p[3]])
            p[0] = p[1]

    def p_arg_seq_2(self, p):
        """s_comm_arg_seq : s_comm_arg_seq NMB NMB NMB NMB
                       | NMB NMB NMB NMB
        q_comm_arg_seq : q_comm_arg_seq NMB NMB NMB NMB
                       | NMB NMB NMB NMB
        """
        if len(p) == 5:
            p[0] = [[p[1], p[2], p[3], p[4]]]
        else:
            p[1].append([p[2], p[3], p[4], p[5]])
            p[0] = p[1]

    def p_arg_seq_3(self, p):
        """c_comm_arg_seq : c_comm_arg_seq NMB NMB NMB NMB NMB NMB
        | NMB NMB NMB NMB NMB NMB
        """
        if len(p) == 7:
            p[0] = [[p[1], p[2], p[3], p[4], p[5], p[6]]]
        else:
            p[1].append([p[2], p[3], p[4], p[5], p[6], p[7]])
            p[0] = p[1]

    def p_arg_seq_4(self, p):
        """h_comm_arg_seq : h_comm_arg_seq NMB
                       | NMB
        v_comm_arg_seq : v_comm_arg_seq NMB
                       | NMB
        """
        if len(p) == 2:
            p[0] = [[p[1]]]
        else:
            p[1].append([p[2]])
            p[0] = p[1]

    def p_arg_seq_5(self, p):
        """a_comm_arg_seq : a_comm_arg_seq a_comm_arg
        | a_comm_arg
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_arg_1(self, p):
        """a_comm_arg : NMB NMB NMB NMB NMB NMB NMB"""
        if (p[4] < 0 or p[4] > 1) or (p[5] < 0 or p[5] > 1):
            raise Exception(
                "One of the 'flags' in elliptical arc is not valid.\n"
                f"It were found in this sequence: {p[1:7]}."
            )
        else:
            p[0] = [abs(p[1]), abs(p[2]), p[3], p[4], p[5], p[6][0], p[6][1]]

    def p_error(self, p):
        raise Exception(
            "Some error happened while 'yacc' were parsing 'd' attribute. "
            "Looks like he encountered incorrect sequence of tokens.\n"
            f"First ten characters from that sequence: {p[0:11]}.\n"
        )

    tokens = ply_lex_d.tokens


class SVGD(SVGContainerEntity):
    """Class for SVG "d" attribute.

    Inherited: no
    """

    # "last_abs_seg": contains "current point". Also
    # almost whole segment is needed for Q, T, S.
    # "last_abs_moveto": last seen absolute moveto command.

    def __init__(self, data):
        super().__init__(data)
        self.ctm = SVGTrafoScale((1, 1)).matrix()
        moveto = SVGDSeg("M", [0, 0])
        self.last_abs_seg = moveto
        self.last_abs_moveto = moveto

    @property
    def dtype(self):
        return "d"

    @classmethod
    def from_raw_data(cls, data):
        lexer = lex(module=ply_lex_d)
        lexer.input(data)
        parser = yacc(module=S2SDYacc(), write_tables=0, debug=False)
        return cls(parser.parse(debug=False, lexer=lexer))

    def process_abs(self, seg):
        ctma, ctmb, ctmc, ctmd, ctme, ctmf = self.ctm.data
        coords = seg.data
        for i in range(0, len(coords), 2):
            x, y = coords[i], coords[i + 1]
            coords[i] = ctma * x + ctmc * y + ctme
            coords[i + 1] = ctmb * x + ctmd * y + ctmf
        return seg

    def process_rel(self, seg):
        cpx, cpy = self.last_abs_seg.data[-2:]
        coords = seg.data
        for i in range(0, len(coords), 2):
            coords[i] += cpx
            coords[i + 1] += cpy
        seg.dtype = seg.dtype.upper()
        return seg

    def get_control_point_unoptimised_reference(self, seg):
        # T & S automatically unpacked to Q & C, hence this statement.
        if self.last_abs_seg.dtype == seg.dtype:
            ctrlp2x, ctrlp2y, cpx, cpy = self.last_abs_seg.data[-4:]
            d = sqrt((cpx - ctrlp2x) ** 2 + (cpy - ctrlp2y) ** 2)
            ctrlp1x = cpx + d * (cpx - ctrlp2x) / d
            ctrlp1y = cpy + d * (cpy - ctrlp2y) / d
            ctrlp1x = (cpx / d) + (cpx - ctrlp2x)
            ctrlp1y = (cpy / d) + (cpy - ctrlp2y)
            ctrlp = [ctrlp1x, ctrlp1y]
        else:
            cpx, cpy = self.last_abs_seg.data[-2:]
            ctrlp = [cpx, cpy]
        return ctrlp

    def get_control_point_optimised_alternative_01(self, seg):
        if self.last_abs_seg.dtype == seg.dtype:
            ctrlp2x, ctrlp2y, cpx, cpy = self.last_abs_seg.data[-4:]
            ctrlp = [2 * cpx - ctrlp2x, 2 * cpy - ctrlp2y]
        else:
            cpx, cpy = self.last_abs_seg.data[-2:]
            ctrlp = [cpx, cpy]
        return ctrlp

    get_control_point = get_control_point_optimised_alternative_01

    # Unique type of command.
    def M(self, seg):
        dcopy = deepcopy(seg)
        self.last_abs_seg = dcopy
        self.last_abs_moveto = dcopy
        return self.process_abs(seg)

    def m(self, seg):
        seg.dtype = "M"
        seg.data[0] += self.last_abs_moveto.data[0]
        seg.data[1] += self.last_abs_moveto.data[1]
        return self.M(seg)

    # Unique type of command.
    def L(self, seg):
        self.last_abs_seg = deepcopy(seg)
        return self.process_abs(seg)

    def l(self, seg):
        return self.L(self.process_rel(seg))

    def H(self, seg):
        seg.dtype = "L"
        seg.data.insert(1, self.last_abs_seg.data[-1])
        return self.L(seg)

    def h(self, seg):
        seg.dtype = "H"
        seg.data[0] += self.last_abs_seg.data[-2]
        return self.H(seg)

    def V(self, seg):
        seg.dtype = "L"
        seg.data.insert(0, self.last_abs_seg.data[-2])
        return self.L(seg)

    def v(self, seg):
        seg.dtype = "V"
        seg.data[0] += self.last_abs_seg.data[-1]
        return self.V(seg)

    # Unique type of command.
    def C(self, seg):
        self.last_abs_seg = deepcopy(seg)
        return self.process_abs(seg)

    def c(self, seg):
        return self.C(self.process_rel(seg))

    def S(self, seg):
        seg.dtype = "C"
        seg.data = self.get_control_point(seg) + seg.data
        return self.C(seg)

    def s(self, seg):
        return self.S(self.process_rel(seg))

    # Unique type of command.
    def Q(self, seg):
        qp0x, qp0y = self.last_abs_seg.data[-2:]
        qp1x, qp1y, qp2x, qp2y = seg.data
        self.last_abs_seg = deepcopy(seg)
        seg.dtype = "C"
        seg.data = [
            qp0x + (2 / 3) * (qp1x - qp0x),
            qp0y + (2 / 3) * (qp1y - qp0y),
            qp2x + (2 / 3) * (qp1x - qp2x),
            qp2y + (2 / 3) * (qp1y - qp2y),
            qp2x,
            qp2y,
        ]
        return self.process_abs(seg)

    def q(self, seg):
        return self.Q(self.process_rel(seg))

    def T(self, seg):
        seg.dtype = "Q"
        seg.data = self.get_control_point(seg) + seg.data
        return self.Q(seg)

    def t(self, seg):
        return self.T(self.process_rel(seg))

    processing_method = dict(
        M=M,
        m=m,
        L=L,
        l=l,
        H=H,
        h=h,
        V=V,
        v=v,
        C=C,
        c=c,
        S=S,
        s=s,
        Q=Q,
        q=q,
        T=T,
        t=t,
    )

    def ssa_repr(self, ssa_repr_config):
        path = [SVGD.processing_method[seg.dtype](self, seg) for seg in self.data]
        if ssa_repr_config["collapse_consecutive_path_segments"] == 1:
            path = collapse_consecutive_objects(path)
        return " ".join(seg.ssa_repr(ssa_repr_config) for seg in path)

    def __add__(self, other):
        return self.__class__(self.data + other.data)
