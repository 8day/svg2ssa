from math import sqrt
from ply.lex import lex
from ply.yacc import yacc
from ..core import SVGContainerEntity
from .transform import SVGTrafoScale


class S2SDLex:
    # All SVG commands.
    literals = "MmLlHhVvCcSsQqTt"

    tokens = ("NMB",)

    t_ignore_WSP = r"[ \t\n\r]"
    t_ignore_COMMA = r","
    t_ignore_CLOSE_PATH = r"[Zz]"

    def t_NMB(t):
        """[+-]?(?:(?:(?:[0-9]+)?\.(?:[0-9]+)|(?:[0-9]+)\.)(?:[eE][+-]?(?:[0-9]+))?|(?:[0-9]+)(?:[eE][+-]?(?:[0-9]+)))|[+-]?(?:[0-9]+)"""
        t.value = float(t.value)
        return t

    def t_error(t):
        # Fixme: When ``t.value[0]`` will be the last character in the sequence, ``t.value[1:11]`` may cause errors.
        raise Exception(
            f"The next illegal character were found in 'd' attribute: '{t.value[0]}'.\n"
            f"These characters were right after it: {t.value[1:11]}"
        )


class S2SDYacc:
    """Class for PLY Yacc for attr ``d``."""

    # Currently support of some instructions disabled on the lexer's level.
    # BTW, there is a difference in SVG whether ``Z`` is present or not: stroke joins are rendered differently. With SSA that is not the case, so I forced lexer to ignore ``Z``'s. In SVG Rec. it's stated: "If you instead "manually" close the subpath via a "lineto" command, the start of the first segment and the end of the last segment are not joined but instead are each capped using the current value of ``stroke-linecap``. At the end of the command, the new current point is set to the initial point of the current subpath."

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
        arg_seqs = p[2]
        for arg_seq in arg_seqs:
            arg_seq.insert(0, comm)
        p[0] = arg_seqs

    def p_comms_2(self, p):
        """m_comm : "M" m_comm_arg_seq
        | "m" m_comm_arg_seq
        """

        mvto, lnto = S2SDYacc.mvto_lnto_mapping[p[1]]
        arg_seqs = p[2]
        arg_seqs[0].insert(0, mvto)
        for i in range(1, len(arg_seqs)):
            arg_seqs[i].insert(0, lnto)
        p[0] = arg_seqs

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

    tokens = S2SDLex.tokens


class SVGD(SVGContainerEntity):
    """Class for SVG ``d`` attribute.

    Inherited: no
    """

    def __init__(self, data):
        super().__init__(data)
        self.ctm = SVGTrafoScale((1, 1)).matrix()

    @property
    def dtype(self):
        return "d"

    @classmethod
    def from_raw_data(cls, data):
        lexer = lex(module=S2SDLex)
        lexer.input(data)
        parser = yacc(module=S2SDYacc(), write_tables=0, debug=False)
        return cls(parser.parse(debug=False, lexer=lexer))

    @staticmethod
    def control_point(last_abs_seg_dtype, last_abs_seg_data, dtype):
        # ``T`` & ``S`` are automatically unpacked to ``Q`` & ``C``, hence this statement.
        if last_abs_seg_dtype == dtype:
            ctrlp2x, ctrlp2y, cpx, cpy = last_abs_seg_data[-4:]
            ctrlp = [2 * cpx - ctrlp2x, 2 * cpy - ctrlp2y]
        else:
            ctrlp = last_abs_seg_data[-2:]
        return ctrlp

    def ssa_repr(self, ssa_repr_config):
        ctma, ctmb, ctmc, ctmd, ctme, ctmf = self.ctm.data
        # ``last_abs_seg_data`` -- contains "current point". Every relative point in a shape depends on a previous absolute point, except relative moveto. Also almost whole segment is needed for ``Q``, ``T``, ``S``.
        # ``last_abs_moveto_data`` -- last seen absolute moveto command. Every relative moveto point in a shape depends on a previous absolute moveto point from previous shape.
        last_abs_seg_dtype = "M"
        last_abs_seg_data = last_abs_moveto_data = [0, 0]
        basic_rel_comms = {"l": "L", "c": "C", "s": "S", "q": "Q", "t": "T"}
        terminal_comms = {"M": "m", "L": "l", "C": "b"}
        segs = []
        for seg in self.data:
            dtype, *data = seg
            while True:
                # Convert rel comms to abs.
                if dtype in basic_rel_comms:
                    dtype = basic_rel_comms[dtype]
                    cpx = last_abs_seg_data[-2]
                    cpy = last_abs_seg_data[-1]
                    for i in range(0, len(data), 2):
                        data[i] += cpx
                        data[i + 1] += cpy

                if dtype == "m":
                    dtype = "M"
                    data[0] += last_abs_moveto_data[0]
                    data[1] += last_abs_moveto_data[1]

                elif dtype == "H":
                    dtype = "L"
                    data.insert(1, last_abs_seg_data[-1])

                elif dtype == "h":
                    dtype = "H"
                    data[0] += last_abs_seg_data[-2]

                elif dtype == "V":
                    dtype = "L"
                    data.insert(0, last_abs_seg_data[-2])

                elif dtype == "v":
                    dtype = "V"
                    data[0] += last_abs_seg_data[-1]

                elif dtype == "S":
                    dtype = "C"
                    data = SVGD.control_point(last_abs_seg_dtype, last_abs_seg_data, dtype) + data

                elif dtype == "Q":
                    qp0x = last_abs_seg_data[-2]
                    qp0y = last_abs_seg_data[-1]
                    qp1x, qp1y, qp2x, qp2y = data
                    dtype = "C"
                    data = [
                        qp0x + (2 / 3) * (qp1x - qp0x),
                        qp0y + (2 / 3) * (qp1y - qp0y),
                        qp2x + (2 / 3) * (qp1x - qp2x),
                        qp2y + (2 / 3) * (qp1y - qp2y),
                        qp2x,
                        qp2y,
                    ]

                elif dtype == "T":
                    dtype = "Q"
                    data = SVGD.control_point(last_abs_seg_dtype, last_abs_seg_data, dtype) + data

                if dtype in terminal_comms:
                    last_abs_seg_dtype = dtype
                    last_abs_seg_data = data
                    if dtype == "M":
                        last_abs_moveto_data = data

                    # Apply CTM to terminal, abs comms.
                    processed = []
                    for i in range(0, len(data), 2):
                        x = data[i]
                        y = data[i + 1]
                        processed.append(str(round(ctma * x + ctmc * y + ctme)))
                        processed.append(str(round(ctmb * x + ctmd * y + ctmf)))

                    # Convert to SSA representation.
                    segs.append(f"{terminal_comms[dtype]} {' '.join(processed)}")
                    break

        return " ".join(segs)
