from dataclasses import dataclass
from typing import Dict, List


# Register ABI names mapped to integer numbers
regmap: Dict[str, int] = {
    "zero": 0,
    "ra": 1,
    "sp": 2,
    "gp": 3,
    "tp": 4,
    "t0": 5,
    "t1": 6,
    "t2": 7,
    "s0": 8,
    "s1": 9,
    "a0": 10,
    "a1": 11,
    "a2": 12,
    "a3": 13,
    "a4": 14,
    "a5": 15,
    "a6": 16,
    "a7": 17,
    "s2": 18,
    "s3": 19,
    "s4": 20,
    "s5": 21,
    "s6": 22,
    "s7": 23,
    "s8": 24,
    "s9": 25,
    "s10": 26,
    "s11": 27,
    "t3": 28,
    "t4": 29,
    "t5": 30,
    "t6": 31,
}


@dataclass
class Instruction:
    pc: int
    next_pc: int
    instr: str
    rd: str
    rs1: str
    rs2: str
    rf: Dict[str, int]

    def is_jr(self) -> int:
        if ("jalr" in self.instr or "jr" in self.instr) and self.rs1 != 1:
            return 1
        return 0

    def __str__(self) -> str:
        return f"{self.pc:#x}    {self.instr}    rd = {self.rd}    rs1 = {self.rs1}    rs2 = {self.rs2}"


@dataclass
class Application:
    name: str
    instructions: List[Instruction]
    cycles: int


def write_rf(rf: Dict[str, int], register: str, value: int) -> None:
    """Update register file"""
    rf[register] = value


def read_rf(rf: Dict[str, int], register: str) -> int:
    """Read register file"""
    try:
        return rf[register]
    except KeyError:
        return 0
