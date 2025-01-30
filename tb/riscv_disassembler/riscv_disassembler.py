"""
Module containing a function for disassembling RISC-V instructions
and functions for each instruction's format.
"""
from dataclasses import dataclass
from typing import Optional

from .riscv_instructions_parser import (
    get_addi4spn_imm,
    get_addi16sp_imm,
    get_b_type_imm,
    get_c_instruction,
    get_cb_offset,
    get_ci_cr_dest_reg,
    get_ci_nzuimm,
    get_ci_sp_imm,
    get_ciw_imm,
    get_cl_cs_imm,
    get_compressed_lui_get_imm,
    get_compressed_rs1,
    get_compressed_rs2_rd,
    get_cr_source_reg,
    get_css_offset,
    get_fdq_instruction,
    get_fence_ps,
    get_funct3,
    get_funct5,
    get_i_type_imm,
    get_i_type_shamt,
    get_instruction,
    get_j_type_imm,
    get_jump_target,
    get_opcode,
    get_r_type_funct7,
    get_rd,
    get_rs1,
    get_rs2,
    get_s_type_imm,
    get_suffix_aqrl,
    get_u_type_imm,
)
from .riscv_instructions_table import (
    C_OPCODES,
    CSR_ADDR,
    FDQ_OPCODES,
    INSTR_FORMAT_BY_OPC,
)


@dataclass
class dsm:
    pc: int
    instr: str
    rd: int
    rs1: int
    rs2: int


def disassemble(instruction: int, pc: int) -> Optional[dsm]:
    """Disassemble any RISC-V instruction covered by the disassembler.

    Parameters
    ----------
    instruction : int
        The instruction to be disassembled.
    pc:
        The Program Counter corresponding to the instruction.
    Returns
    ------
    str
        The disassembly of the instruction.

    Examples
    --------
    >>> print(disassemble(0xfc448493,0x10000040))
    addi     x9,x9,-60
    >>> print(disassemble(4232348819,268435520))
    addi     x9,x9,-60

    """
    opcode: Optional[int] = get_opcode(instruction)

    if opcode not in INSTR_FORMAT_BY_OPC or opcode is None:
        return None

    if opcode in C_OPCODES:
        instr_mnemonic, instr_format = get_c_instruction(instruction, opcode)
    elif opcode in FDQ_OPCODES:
        instr_mnemonic = get_fdq_instruction(instruction, opcode)
        instr_format = "FDQ"
    else:
        instr_mnemonic = get_instruction(instruction, opcode)
        instr_format = INSTR_FORMAT_BY_OPC[opcode]

    if instr_mnemonic is None or instr_format is None:
        return None

    # Immediate type
    if instr_format == "I":
        return _i_format_analysis(instruction, pc, opcode, instr_mnemonic)

    # Register type
    elif instr_format == "R":
        return _r_format_analysis(instruction, pc, opcode, instr_mnemonic)

    # Four Registers type
    elif instr_format == "R4":
        return _r4_format_analysis(instruction, pc, instr_mnemonic)

    # Store type
    elif instr_format == "S":
        return _s_format_analysis(instruction, pc, instr_mnemonic)

    # Branch type
    elif instr_format == "B":
        return _b_format_analysis(instruction, pc, instr_mnemonic)

    # Upper immediate type
    elif instr_format == "U":
        return _u_format_analysis(instruction, pc, instr_mnemonic)

    # Jump type
    elif instr_format == "J":
        return _j_format_analysis(instruction, pc, instr_mnemonic)

    # Jump type
    elif instr_format == "FDQ":
        return _fdq_format_analysis(instruction, pc, opcode, instr_mnemonic)

    # Compressed Register
    elif instr_format == "CR":
        return _cr_format_analysis(instruction, pc, instr_mnemonic)

    # Compressed Immediate
    elif instr_format == "CI":
        return _ci_format_analysis(instruction, pc, instr_mnemonic)

    # Compressed Stack-rative Store
    elif instr_format == "CSS":
        return _css_format_analysis(instruction, pc, instr_mnemonic)

    # Compressed Wide Immediate
    elif instr_format == "CIW":
        return _ciw_format_analysis(instruction, pc, instr_mnemonic)

    # Compressed Load
    elif instr_format == "CL":
        return _cl_format_analysis(instruction, pc, instr_mnemonic)

    # Compressed Store
    elif instr_format == "CS":
        return _cs_format_analysis(instruction, pc, instr_mnemonic)

    # Compressed Arithmetic
    elif instr_format == "CA":
        return _ca_format_analysis(instruction, pc, instr_mnemonic)

    # Compressed Branch
    elif instr_format == "CB":
        return _cb_format_analysis(instruction, pc, instr_mnemonic)

    # Compressed Jump
    elif instr_format == "CJ":
        return _cj_format_analysis(instruction, pc, instr_mnemonic)

    else:
        assert (
            False
        ), f"Unable to find a disassembly for format {instr_mnemonic} associated with format {instr_format}."


""" Instruction's format analysis"""


def _i_format_analysis(
    instruction: int, pc: int, opcode: int, instr_mnemonic: str
) -> dsm:
    rs1: int = get_rs1(instruction)
    rd: int = get_rd(instruction)
    funct3: int = get_funct3(instruction)
    i_imm: int = get_i_type_imm(instruction, is_signed=True)

    instr_str: str = f"{instr_mnemonic} \t x{rd},x{rs1},{i_imm:#x}"

    # Conditions to adapt to all the different formats
    if opcode in [0x3, 0x67]:
        instr_str = f"{instr_mnemonic} \t x{rd},{i_imm}(x{rs1})"
        return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)

    if opcode == 0xF:
        if funct3 == 0x0:
            P, S = get_fence_ps(instruction)
            if P == "pause" or S == "pause":
                instr_str = "pause"
                return dsm(pc=pc, instr=instr_str, rd=0, rs1=0, rs2=0)

            instr_str = f"{instr_mnemonic} \t {P},{S}"
            return dsm(pc=pc, instr=instr_str, rd=0, rs1=0, rs2=0)

        if funct3 == 0x1:
            instr_str = f"{instr_mnemonic}"
            return dsm(pc=pc, instr=instr_str, rd=0, rs1=0, rs2=0)

    if opcode in [0x13, 0x1B]:
        if funct3 in [0x0, 0x4, 0x6, 0x7]:
            instr_str = f"{instr_mnemonic} \t x{rd},x{rs1},{i_imm}"
            return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)

        if funct3 == 0x5:
            shamt = get_i_type_shamt(instruction)
            instr_str = f"{instr_mnemonic} \t x{rd},x{rs1},{shamt:#x}"
            return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)

        if funct3 in [0x2, 0x3]:
            instr_str = f"{instr_mnemonic} \t x{rd},x{rs1},{i_imm}"
            return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)

    if opcode == 0x73:
        i_imm = get_i_type_imm(instruction, is_signed=False)
        if funct3 in [0x1, 0x2, 0x3]:
            csr = CSR_ADDR[i_imm]
            instr_str = f"{instr_mnemonic} \t x{rd},{csr},x{rs1}"
            return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)

        if funct3 in [0x5, 0x6, 0x7]:
            csr = CSR_ADDR[i_imm]
            instr_str = f"{instr_mnemonic} \t x{rd},{csr},{rs1}"
            return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)

        if funct3 in [0x0, 0x4]:
            if i_imm == 0xFC0:
                instr_str = f"{instr_mnemonic} \t x{rs1}"
                return dsm(pc=pc, instr=instr_str, rd=0, rs1=rs1, rs2=0)
            instr_str = f"{instr_mnemonic}"
            return dsm(pc=pc, instr=instr_str, rd=0, rs1=0, rs2=0)

    return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)


def _r_format_analysis(
    instruction: int, pc: int, opcode: int, instr_mnemonic: str
) -> dsm:
    rs1: int = get_rs1(instruction)
    rs2: int = get_rs2(instruction)
    rd: int = get_rd(instruction)

    instr_str: str = f"{instr_mnemonic} \t x{rd},x{rs1},x{rs2}"

    if opcode == 0x2F:  # RV32A opcode
        if instr_mnemonic in ["lr.w", "lr.d"]:
            instr_str = (
                f"{instr_mnemonic}{get_suffix_aqrl(instruction)} \t x{rd},(x{rs1})"
            )
            return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)

        instr_str = (
            f"{instr_mnemonic}{get_suffix_aqrl(instruction)} \t x{rd},x{rs2},(x{rs1})"
        )
        return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=rs2)

    return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=rs2)


def _r4_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rs1: int = get_rs1(instruction)
    rs2: int = get_rs2(instruction)
    rs3: int = get_funct5(instruction)
    rd: int = get_rd(instruction)
    instr_str: str = f"{instr_mnemonic} \t x{rd},x{rs1},x{rs2},x{rs3}"

    return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=rs2)


def _s_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rs1: int = get_rs1(instruction)
    rs2: int = get_rs2(instruction)
    s_imm: int = get_s_type_imm(instruction)
    instr_str: str = f"{instr_mnemonic} \t x{rs2},{s_imm}(x{rs1})"

    return dsm(pc=pc, instr=instr_str, rd=0, rs1=rs1, rs2=rs2)


def _b_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rs1: int = get_rs1(instruction)
    rs2: int = get_rs2(instruction)
    b_imm: int = get_b_type_imm(instruction)
    branch_value: int = pc + b_imm
    instr_str: str = f"{instr_mnemonic} \t x{rs1},x{rs2},{branch_value:x}"

    return dsm(pc=pc, instr=instr_str, rd=0, rs1=rs1, rs2=rs2)


def _u_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rd: int = get_rd(instruction)
    u_imm: int = get_u_type_imm(instruction)
    instr_str: str = f"{instr_mnemonic} \t x{rd},{u_imm:#x}"

    return dsm(pc=pc, instr=instr_str, rd=rd, rs1=0, rs2=0)


def _j_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rd: int = get_rd(instruction)
    j_imm: int = get_j_type_imm(instruction)
    jpt: int = j_imm + pc
    instr_str: str = f"{instr_mnemonic} \t x{rd},{jpt:x}"

    return dsm(pc=pc, instr=instr_str, rd=rd, rs1=0, rs2=0)


def _fdq_format_analysis(
    instruction: int, pc: int, opcode: int, instr_mnemonic: str
) -> dsm:
    rs1: int = get_rs1(instruction)
    rs2: int = get_rs2(instruction)
    rd: int = get_rd(instruction)
    i_imm: int = get_i_type_imm(instruction, is_signed=True)

    # Conditions to adapt to all the different formats
    if opcode == 0x7:
        instr_str = f"{instr_mnemonic} \t x{rd},{i_imm}(x{rs1})"
        return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)

    if opcode == 0x27:
        s_imm: int = get_s_type_imm(instruction)
        instr_str = f"{instr_mnemonic} \t x{rs2},{s_imm}(x{rs1})"
        return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)

    if opcode in [0x43, 0x47, 0x4B, 0x4F]:
        rs3: int = get_funct3(instruction)
        instr_str: str = f"{instr_mnemonic} \t x{rd},x{rs1},x{rs2},x{rs3}"
        return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=rs2)

    instr_str: str = f"{instr_mnemonic} \t x{rd},x{rs1},{i_imm:#x}"

    if get_r_type_funct7(instruction) in [
        0x0,
        0x1,
        0x2,
        0x3,
        0x4,
        0x5,
        0x7,
        0x8,
        0x9,
        0xA,
        0xC,
        0xD,
        0xF,
        0x10,
        0x11,
        0x13,
        0x14,
        0x15,
        0x17,
        0x50,
        0x51,
        0x53,
    ]:
        instr_str: str = f"{instr_mnemonic} \t x{rd},x{rs1},x{rs2}"

    return dsm(pc=pc, instr=instr_str, rd=rd, rs1=rs1, rs2=0)


def _cr_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rd_rs1: int = get_ci_cr_dest_reg(instruction)
    rs2: int = get_cr_source_reg(instruction)

    instr_str: str = f"{instr_mnemonic} \t x{rd_rs1}"

    if instr_mnemonic == "c.mv" or instr_mnemonic == "c.add":
        instr_str = f"{instr_mnemonic} \t x{rd_rs1},x{rs2}"
        return dsm(pc=pc, instr=instr_str, rd=rd_rs1, rs1=rd_rs1, rs2=rs2)

    # c.ebreak
    if instruction == 0x9002:
        instr_str = f"{instr_mnemonic}"
        return dsm(pc=pc, instr=instr_str, rd=0, rs1=0, rs2=0)

    return dsm(pc=pc, instr=instr_str, rd=0, rs1=rd_rs1, rs2=0)


def _ci_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rd_rs1: int = get_ci_cr_dest_reg(instruction)
    nzuimm: int = get_ci_nzuimm(instruction, is_signed=True)

    instr_str: str = f"{instr_mnemonic} \t x{rd_rs1},{nzuimm:#x}"

    if instr_mnemonic == "c.lui":
        ns_nzuimm: int = get_compressed_lui_get_imm(
            get_ci_nzuimm(instruction, is_signed=False)
        )
        instr_str = f"{instr_mnemonic} \t x{rd_rs1},{ns_nzuimm:#x}"
        return dsm(pc=pc, instr=instr_str, rd=rd_rs1, rs1=rd_rs1, rs2=0)

    if instr_mnemonic == "c.li":
        instr_str = f"{instr_mnemonic} \t x{rd_rs1},{nzuimm}"
        return dsm(pc=pc, instr=instr_str, rd=rd_rs1, rs1=rd_rs1, rs2=0)

    if "sp" in instr_mnemonic:
        if "16" in instr_mnemonic:
            nzuimm = get_addi16sp_imm(instruction)
            instr_str = f"{instr_mnemonic} \t x{rd_rs1},{nzuimm}"
            return dsm(pc=pc, instr=instr_str, rd=rd_rs1, rs1=rd_rs1, rs2=0)

        imm: int = get_ci_sp_imm(instruction)
        instr_str = f"{instr_mnemonic} \t x{rd_rs1},{imm}(x2)"
        return dsm(pc=pc, instr=instr_str, rd=rd_rs1, rs1=2, rs2=0)

    if instr_mnemonic in ["c.addi", "c.addiw"]:
        instr_str = f"{instr_mnemonic} \t x{rd_rs1},{nzuimm}"
        return dsm(pc=pc, instr=instr_str, rd=rd_rs1, rs1=rd_rs1, rs2=0)

    if instr_mnemonic in ["c.slli", "c.slli64"]:
        nzuimm = get_ci_nzuimm(instruction, is_signed=False)
        instr_str = f"{instr_mnemonic} \t x{rd_rs1},{nzuimm:#x}"
        return dsm(pc=pc, instr=instr_str, rd=rd_rs1, rs1=rd_rs1, rs2=0)

    return dsm(pc=pc, instr=instr_str, rd=rd_rs1, rs1=rd_rs1, rs2=0)


def _css_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rs2: int = get_cr_source_reg(instruction)
    offset: int = get_css_offset(instruction)
    instr_str: str = f"{instr_mnemonic} \t x{rs2},{offset}(x2)"

    return dsm(pc=pc, instr=instr_str, rd=0, rs1=2, rs2=rs2)


def _ciw_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    imm: int = get_ciw_imm(instruction)
    rd_p: int = get_compressed_rs2_rd(instruction)

    instr_str: str = f"{instr_mnemonic} \t x{rd_p},x2,{imm}"

    if instr_mnemonic == "c.addi4spn":
        imm = get_addi4spn_imm(instruction)
        if imm == 0:
            instr_str = "c.unimp"
            return dsm(pc=pc, instr=instr_str, rd=0, rs1=0, rs2=0)
        instr_str = f"{instr_mnemonic} \t x{rd_p},x2,{imm}"
        return dsm(pc=pc, instr=instr_str, rd=rd_p, rs1=2, rs2=0)

    return dsm(pc=pc, instr=instr_str, rd=rd_p, rs1=2, rs2=0)


def _cl_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rd_p: int = get_compressed_rs2_rd(instruction)
    rs1_p: int = get_compressed_rs1(instruction)
    offset: int = get_cl_cs_imm(instruction)
    instr_str: str = f"{instr_mnemonic} \t x{rd_p},{offset}(x{rs1_p})"

    return dsm(pc=pc, instr=instr_str, rd=rd_p, rs1=rs1_p, rs2=0)


def _cs_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rs1_p: int = get_compressed_rs1(instruction)
    rs2_p: int = get_compressed_rs2_rd(instruction)
    imm: int = get_cl_cs_imm(instruction)
    instr_str: str = f"{instr_mnemonic} \t x{rs2_p},{imm}(x{rs1_p})"

    return dsm(pc=pc, instr=instr_str, rd=0, rs1=rs1_p, rs2=rs2_p)


def _ca_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rd_p: int = get_compressed_rs1(instruction)
    rs2_p: int = get_compressed_rs2_rd(instruction)
    instr_str: str = f"{instr_mnemonic} \t x{rd_p},x{rs2_p}"

    return dsm(pc=pc, instr=instr_str, rd=rd_p, rs1=rs2_p, rs2=0)


def _cb_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    rs1_p: int = get_compressed_rs1(instruction)

    offset: int = get_cb_offset(instruction)
    branch_value: int = offset + pc
    instr_str: str = f"{instr_mnemonic} \t x{rs1_p},{branch_value:x}"

    if instr_mnemonic == "c.andi":
        imm: int = get_ci_nzuimm(instruction, is_signed=True)
        instr_str = f"{instr_mnemonic} \t x{rs1_p},{imm}"
        return dsm(pc=pc, instr=instr_str, rd=0, rs1=rs1_p, rs2=0)

    if instr_mnemonic in ["c.srai", "c.srai64", "c.srli", "c.srli64"]:
        imm = get_ci_nzuimm(instruction, is_signed=False)
        instr_str = f"{instr_mnemonic} \t x{rs1_p},{imm:#x}"
        return dsm(pc=pc, instr=instr_str, rd=0, rs1=rs1_p, rs2=0)

    return dsm(pc=pc, instr=instr_str, rd=0, rs1=rs1_p, rs2=0)


def _cj_format_analysis(instruction: int, pc: int, instr_mnemonic: str) -> dsm:
    jpt: int = get_jump_target(instruction) + pc
    instr_str: str = f"{instr_mnemonic} \t {jpt:x}"

    return dsm(pc=pc, instr=instr_str, rd=0, rs1=0, rs2=0)
