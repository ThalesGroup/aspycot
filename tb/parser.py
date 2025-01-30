import logging
import os
import sys
from typing import Dict, List, Optional

from arch import Instruction, write_rf
from riscv_disassembler import disassemble, dsm
from runner import sw_dir
from vendor.spike_log_to_trace_csv import read_spike_trace

_logger: logging.Logger = logging.getLogger("aspycot.parser")
_logger.setLevel(4)


def get_apps_path() -> Dict[str, str]:
    """Based on environment variables, retrieve paths of the apps to parse."""

    bmarks: str = os.getenv("ASPYCOT_BMARKS", "hello_world")

    apps: List[str] = bmarks.split(",")
    traces: Dict[str, str] = {}

    for app in apps:
        trace: str = os.path.join(sw_dir, f"build/{app}/{app}.riscv.log")

        if not os.path.isfile(trace):
            _logger.info(f"Trace file for {app} does not exist: {trace}.")
            sys.exit(1)

        traces[app] = trace

    return traces


def get_app_instr(path: str):
    """Process SPIKE simulation log.

    Extract instruction and affected register information from spike simulation
    log and write the results to a CSV file at csv. Returns the number of
    instructions written.

    This function is an adaptation of Google script to parse Spike logs to CSV.

    """

    _logger.info("Processing spike log : {}".format(path))

    instruction: Optional[Instruction] = None
    rf: Dict[str, int] = {}

    total_insns: int = 0

    for entry, _ in read_spike_trace(path, 1):
        total_insns += 1

        if total_insns != 1:
            instruction = Instruction(
                pc=int(pc, 16),
                next_pc=int(entry.pc, 16),
                instr=disassembled.instr,
                rd=disassembled.rd,
                rs1=disassembled.rs1,
                rs2=disassembled.rs2,
                rf=rf,
            )

        pc = entry.pc
        instr = entry.instr
        gpr = entry.gpr
        binary = entry.binary

        disassembled: Optional[dsm] = disassemble(int(binary, 16), int(pc, 16))

        if not disassembled:
            _logger.error(f"Unsupported instruction: {instr}")
            sys.exit(1)

        # If there is a GPR update, process it
        if gpr:
            for g in gpr:
                reg, val = g.split(":")
                write_rf(rf, reg, val)

        if instruction is not None:
            yield instruction, total_insns
