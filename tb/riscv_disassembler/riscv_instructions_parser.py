"""
Module containing functions to extract data from
RISC-V instructions and compressed instructions.
Also contains useful functions to manipulate bits.
"""

import math
from typing import Optional, Tuple

from .riscv_instructions_table import (
    C_INSTR_BY_CODES,
    CSR_ADDR,
    FDQ_INSTR_BY_CODES,
    INSTR_BY_CODES,
)


def get_sign_extended_value(value: int) -> int:
    # Looking for the directly superior 2**p such as value < 2**p
    p = math.ceil(math.log2(value))

    if value - 2**p == 0:
        return -(2**p)
    return value - 2**p


""" Methods for RV32/RV64 instructions """


def get_instruction(instr: int, opc: int) -> Optional[str]:
    if opc not in INSTR_BY_CODES:
        return None

    init_table = INSTR_BY_CODES[opc]

    if opc in [0x17, 0x37, 0x67, 0x6F]:
        assert type(init_table) == str
        return init_table

    assert type(init_table) == dict

    if opc in [0x13, 0x1B]:
        funct3 = get_funct3(instr)
        try:
            second_table = init_table[funct3]
        except KeyError:
            return None
        if type(second_table) == str:
            return second_table
        imm = get_i_type_imm(instr, is_signed=False)
        if funct3 == 5:
            if imm >= 1000:
                # srai, sraiw
                return second_table[32]
            # srli, srliw
            return second_table[0]

        return (second_table[0], second_table[1])

    if opc in [0x3, 0xF, 0x23, 0x63]:
        funct3 = get_funct3(instr)
        return init_table[funct3] if funct3 in init_table else None

    # RV32A / RV64A
    if opc == 0x2F:
        funct3 = get_funct3(instr)
        try:
            second_table = init_table[funct3]
        except KeyError:
            return None
        if type(second_table) == str:
            return second_table
        f5 = get_funct5(instr)
        return second_table[f5] if f5 in second_table else None

    # For Register format
    if opc in [0x33, 0x3B]:
        funct3 = get_funct3(instr)
        try:
            second_table = init_table[funct3]
        except KeyError:
            return None
        if type(second_table) == str:
            return second_table
        funct7 = get_r_type_funct7(instr)
        return second_table[funct7] if funct7 in second_table else None

    if opc == 0x73:
        funct3 = get_funct3(instr)
        imm = get_i_type_imm(instr, is_signed=False)
        try:
            second_table = init_table[funct3]
        except KeyError:
            return None
        if type(second_table) == str:
            if imm not in CSR_ADDR:
                return None
            return second_table

        if funct3 in [0x0, 0x4]:
            funct7 = get_r_type_funct7(instr)
            if funct7 in second_table and funct7 != 0x0:
                return second_table[funct7]

            return second_table[imm] if imm in second_table else None

        return second_table

    return None


def get_c_instruction(instr: int, opc: int) -> Optional[Tuple[str, str]]:
    if opc not in C_INSTR_BY_CODES:
        return None

    init_table = C_INSTR_BY_CODES[opc]

    assert type(init_table) == dict

    if opc == 0x0:
        f3 = get_compressed_funct3(instr)
        return init_table[f3] if f3 in init_table else None

    if opc == 0x1:
        f3 = get_compressed_funct3(instr)
        if f3 not in init_table:
            return None
        second_table = init_table[f3]
        rd = get_ci_cr_dest_reg(instr)
        if f3 == 1:
            if rd == 0:
                # c.addiw
                return second_table[0]
            # c.jal
            return second_table[1]
        if f3 == 3:
            if rd == 2:
                # c.addi16sp
                return second_table[2]
            # c.lui
            return second_table[1]
        if f3 == 4:
            f6 = get_compressed_funct6(instr)
            if f6 not in second_table:
                return None
            third_table = second_table[f6]
            if f6 == 0x20 or f6 == 0x21:
                nzuimm = get_ci_nzuimm(instr, is_signed=True)
                if nzuimm == 0:
                    # c.srli64, c.srai64
                    return third_table[0]
                # c.srli, c.srai
                return third_table[1]
            if f6 == 0x23 or f6 == 0x27:
                f2 = get_compressed_funct2(instr)
                return third_table[f2] if f2 in third_table else None

            return third_table

        return init_table[f3]

    if opc == 0x2:
        f3 = get_compressed_funct3(instr)
        if f3 not in init_table:
            return None
        second_table = init_table[f3]
        if f3 == 0x0:
            nzuimm = get_ci_nzuimm(instr, is_signed=False)
            if nzuimm == 0:
                # c.slli64
                return second_table[0]
            # c.slli
            return second_table[1]

        if f3 == 0x4:
            f4 = get_compressed_funct4(instr)
            if f4 not in second_table:
                return None
            third_table = second_table[f4]
            rs = get_cr_source_reg(instr)
            if f4 == 0x8:
                if rs == 0:
                    # c.jr
                    return third_table[0]
                # c.mv
                return third_table[1]

            if f4 == 0x9:
                rd = get_ci_cr_dest_reg(instr)
                if rs == 0:
                    fourth_table = third_table[rs]
                    if rd == 0:
                        # c.ebreak
                        return fourth_table[0]
                    # c.jalr
                    return fourth_table[1]
                # c.add
                return third_table[1]
            return None
        return init_table[f3] if f3 in init_table else None

    return None


def get_fdq_instruction(instr: int, opc: int) -> Optional[str]:
    if opc not in FDQ_INSTR_BY_CODES:
        return None

    init_table = FDQ_INSTR_BY_CODES[opc]

    assert type(init_table) == dict

    if opc in [0x7, 0x27]:
        funct3 = get_funct3(instr)
        return init_table[funct3] if funct3 in init_table else None

    if opc in [0x43, 0x47, 0x4B, 0x4F]:
        funct2 = get_funct2(instr)
        return init_table[funct2] if funct2 in init_table else None

    if opc == 0x53:
        imm = 0
        funct7 = get_r_type_funct7(instr)

        try:
            second_table = init_table[funct7]
            return second_table
        except KeyError:
            try:
                imm = get_i_type_imm(instr, is_signed=False)
                second_table = init_table[imm]
            except KeyError:
                return None

        if imm == 0:
            if funct7 in range(0x0, 0x10) and funct7 not in [0x2, 0x6, 0xB, 0xE]:
                assert type(init_table[funct7]) == str, f"{funct7}"
                return init_table[funct7] if funct7 in init_table else None
            if funct7 in range(0x10, 0x18) and funct7 not in [0x12, 0x16]:
                funct3 = get_funct3(instr)
                return second_table[funct3] if funct3 in second_table else None
            return None

        if type(second_table) == str:
            return second_table

        funct3 = get_funct3(instr)
        return second_table[funct3] if funct3 in second_table else None


def get_opcode(instruction: int) -> Optional[int]:
    # Compressed instructions use a 2 bit opcode.
    if instruction & 0x3 < 0x3 and instruction < 0xFFFF:
        return instruction & 0x3

    # All non-compressed instructions use a 7 bit opcode ending in 0b11.
    return instruction & 0x7F if instruction < 0xFFFFFFFF else None


def get_funct2(instruction: int) -> int:
    return (0x6000000 & instruction) >> 25


def get_funct3(instruction: int) -> int:
    return (0x7000 & instruction) >> 12


def get_funct5(instruction: int) -> int:
    return (0xF8000000 & instruction) >> 27


def get_r_type_funct7(instruction: int) -> int:
    return (0xFE000000 & instruction) >> 25


def get_rs1(instruction: int) -> int:
    return (0xF8000 & instruction) >> 15


def get_rs2(instruction: int) -> int:
    return (0x1F00000 & instruction) >> 20


def get_rd(instruction: int) -> int:
    return (0xF80 & instruction) >> 7


def get_i_type_imm(instruction: int, is_signed: bool) -> int:
    imm_20 = (0x80000000 & instruction) >> 20
    imm_19_12 = (0x7FF00000 & instruction) >> 20

    imm = imm_20 | imm_19_12

    # Sign extended
    if is_signed and imm_20 != 0:
        imm = get_sign_extended_value(imm)
    return imm


def get_i_type_shamt(instruction: int) -> int:
    return (0x3F00000 & instruction) >> 20


def get_s_type_imm(instruction: int) -> int:
    imm_11 = (0x80000000 & instruction) >> 20
    imm_10_5 = (0x7E000000 & instruction) >> 20
    imm_4_0 = (0xF80 & instruction) >> 7

    imm = imm_11 | imm_10_5 | imm_4_0

    # Sign extended
    if imm_11 != 0:
        imm = get_sign_extended_value(imm)
    return imm


def get_b_type_imm(instruction: int) -> int:
    imm_12 = (0x80000000 & instruction) >> 19
    imm_11 = (0x80 & instruction) << 4
    imm_10_5 = (0x7E000000 & instruction) >> 20
    imm_4_1 = (0xF00 & instruction) >> 7

    imm = imm_12 | imm_11 | imm_10_5 | imm_4_1

    # Sign extended
    if imm_12 != 0:
        imm = get_sign_extended_value(imm)

    return imm


def get_u_type_imm(instruction: int) -> int:
    return (0xFFFFF000 & instruction) >> 12


def get_j_type_imm(instruction: int) -> int:
    imm_20 = (0x80000000 & instruction) >> 11
    imm_10_1 = (0x7FE00000 & instruction) >> 20
    imm_11 = (0x100000 & instruction) >> 9
    imm_19_12 = 0xFF000 & instruction

    imm = imm_20 | imm_10_1 | imm_11 | imm_19_12

    # Sign extended
    if imm_20 != 0:
        imm = get_sign_extended_value(imm)
    return imm


def get_jump_target(instruction: int) -> int:
    jpt_11 = (0x1000 & instruction) >> 1
    jpt_10 = (0x100 & instruction) << 2
    jpt_9_8 = (0x600 & instruction) >> 1
    jpt_7 = (0x40 & instruction) << 1
    jpt_6 = (0x80 & instruction) >> 1
    jpt_5 = (0x4 & instruction) << 3
    jpt_4 = (0x800 & instruction) >> 7
    jpt_3_1 = (0x38 & instruction) >> 2

    jpt = jpt_11 | jpt_10 | jpt_9_8 | jpt_7 | jpt_6 | jpt_5 | jpt_4 | jpt_3_1

    # Sign extended
    if jpt_11 != 0:
        jpt = get_sign_extended_value(jpt)

    return jpt


def get_addi4spn_imm(instruction: int) -> int:
    imm_9_6 = (0x780 & instruction) >> 1
    imm_5_4 = (0x1800 & instruction) >> 7
    imm_3 = (0x20 & instruction) >> 2
    imm_2 = (0x40 & instruction) >> 4

    imm = imm_9_6 | imm_5_4 | imm_3 | imm_2

    return imm


def get_addi16sp_imm(instruction: int) -> int:
    imm_9 = (0x1000 & instruction) >> 3
    imm_8_7 = (0x18 & instruction) << 4
    imm_6 = (0x20 & instruction) << 1
    imm_5 = (0x4 & instruction) << 3
    imm_4 = (0x40 & instruction) >> 2

    imm = imm_9 | imm_8_7 | imm_6 | imm_5 | imm_4

    # Sign-extended
    if imm_9 != 0:
        imm = get_sign_extended_value(imm)

    return imm


def get_fence_ps(instruction: int) -> Tuple[str, str]:
    fence_table = {
        0: "pause",
        1: "w",
        2: "r",
        3: "rw",
        4: "o",
        5: "ow",
        6: "or",
        7: "orw",
        8: "o",
        9: "iw",
        10: "ir",
        11: "irw",
        12: "io",
        13: "iow",
        14: "ior",
        15: "iorw",
    }

    p_bits = (0xF000000 & instruction) >> 24
    s_bits = (0xF00000 & instruction) >> 20

    return (fence_table[p_bits], fence_table[s_bits])


def get_suffix_aqrl(instruction: int) -> str:
    aq = (0x4000000 & instruction) >> 26
    rl = (0x2000000 & instruction) >> 25
    if aq == 1 and rl == 1:
        return ".aqrl"
    if aq == 1 and rl != 1:
        return ".aq"
    if rl == 1 and aq != 1:
        return ".rl"
    return ""


""" Methods for Compressed instructions """


def get_compressed_funct2(instruction: int) -> int:
    return (0x60 & instruction) >> 5


def get_compressed_funct3(instruction: int) -> int:
    return (0xE000 & instruction) >> 13


def get_compressed_funct4(instruction: int) -> int:
    return (0xF000 & instruction) >> 12


def get_compressed_funct6(instruction: int) -> int:
    return (0xFC00 & instruction) >> 10


def get_ci_cr_dest_reg(instruction: int) -> int:
    return (0xF80 & instruction) >> 7


def get_cr_source_reg(instruction: int) -> int:
    return (0x7C & instruction) >> 2


def get_css_offset(instruction: int) -> int:
    funct3 = get_compressed_funct3(instruction)
    imm = 0

    if funct3 == 0x7:
        imm_3 = (0x400 & instruction) >> 7
        imm_4 = (0x800 & instruction) >> 7
        imm_5 = (0x1000 & instruction) >> 7
        imm_6 = (0x80 & instruction) >> 1
        imm_7 = (0x100 & instruction) >> 1
        imm_8 = (0x200 & instruction) >> 1

        imm = imm_8 | imm_7 | imm_6 | imm_5 | imm_4 | imm_3

    elif funct3 == 0x6:
        imm_2 = (0x200 & instruction) >> 7
        imm_3 = (0x400 & instruction) >> 7
        imm_4 = (0x800 & instruction) >> 7
        imm_5 = (0x1000 & instruction) >> 7
        imm_6 = (0x80 & instruction) >> 1
        imm_7 = (0x100 & instruction) >> 1

        imm = imm_7 | imm_6 | imm_5 | imm_4 | imm_3 | imm_2

    elif funct3 == 0x5:
        imm_4 = (0x800 & instruction) >> 7
        imm_5 = (0x1000 & instruction) >> 7
        imm_6 = (0x80 & instruction) >> 1
        imm_7 = (0x100 & instruction) >> 1
        imm_8 = (0x200 & instruction) >> 1
        imm_9 = (0x400 & instruction) >> 1

        imm = imm_9 | imm_8 | imm_7 | imm_6 | imm_5 | imm_4

    return imm


def get_cb_offset(instruction: int) -> int:
    ofs_8 = (0x1000 & instruction) >> 4
    ofs_7_6 = (0x60 & instruction) << 1
    ofs_5 = (0x4 & instruction) << 3
    ofs_4_3 = (0xC00 & instruction) >> 7
    ofs_2_1 = (0x18 & instruction) >> 2

    ofs = ofs_8 | ofs_7_6 | ofs_5 | ofs_4_3 | ofs_2_1

    # Sign extended
    if ofs_8 != 0:
        ofs = get_sign_extended_value(ofs)

    return ofs


def get_ci_nzuimm(instruction: int, is_signed: bool) -> int:
    nzuimm_5 = (0x1000 & instruction) >> 7
    nzuimm_4_0 = (0x7C & instruction) >> 2

    nzuimm = nzuimm_5 | nzuimm_4_0

    # Sign extended
    if is_signed and nzuimm_5 != 0:
        nzuimm = get_sign_extended_value(nzuimm)

    return nzuimm


def get_compressed_lui_get_imm(nzuimm: int) -> int:
    # See c.lui on RISC V manual
    imm = nzuimm << 12
    if imm > 2**17:
        imm += 0xFFFC0000
    return imm >> 12


def get_ci_sp_imm(instruction: int) -> int:
    funct3 = get_compressed_funct3(instruction)

    if funct3 == 0x3:
        imm_3 = (0x20 & instruction) >> 2
        imm_4 = (0x40 & instruction) >> 2
        imm_5 = (0x1000 & instruction) >> 7
        imm_6 = (0x4 & instruction) << 4
        imm_7 = (0x8 & instruction) << 4
        imm_8 = (0x10 & instruction) << 4

        return imm_8 | imm_7 | imm_6 | imm_5 | imm_4 | imm_3

    elif funct3 == 0x2:
        imm_2 = (0x10 & instruction) >> 2
        imm_3 = (0x20 & instruction) >> 2
        imm_4 = (0x40 & instruction) >> 2
        imm_5 = (0x1000 & instruction) >> 7
        imm_6 = (0x4 & instruction) << 4
        imm_7 = (0x8 & instruction) << 4

        return imm_7 | imm_6 | imm_5 | imm_4 | imm_3 | imm_2

    elif funct3 == 0x1:
        imm_4 = (0x40 & instruction) >> 2
        imm_5 = (0x1000 & instruction) >> 7
        imm_6 = (0x4 & instruction) << 4
        imm_7 = (0x8 & instruction) << 4
        imm_8 = (0x10 & instruction) << 4
        imm_9 = (0x20 & instruction) << 4

        return imm_9 | imm_8 | imm_7 | imm_6 | imm_5 | imm_4

    else:
        assert False


def get_ciw_imm(instruction: int) -> int:
    return (0x1FE0 & instruction) >> 5


def get_cl_cs_imm(instruction: int) -> int:
    funct3 = get_compressed_funct3(instruction)
    imm = 0

    if funct3 == 0x3 or funct3 == 0x7:
        imm_5_3 = (0x1C00 & instruction) >> 7
        imm_6 = (0x20 & instruction) << 1
        imm_7 = (0x40 & instruction) << 1

        imm = imm_7 | imm_6 | imm_5_3

    elif funct3 == 0x2 or funct3 == 0x6:
        imm_5_3 = (0x1C00 & instruction) >> 7
        imm_2 = (0x40 & instruction) >> 4
        imm_6 = (0x20 & instruction) << 1

        imm = imm_6 | imm_5_3 | imm_2

    return imm


def get_compressed_rs1(instruction: int) -> int:
    return ((0x380 & instruction) >> 7) + 8


def get_compressed_rs2_rd(instruction: int) -> int:
    return ((0x1C & instruction) >> 2) + 8
