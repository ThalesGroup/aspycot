import os
import sys
from typing import Dict, List

from cocotb.runner import Simulator, get_runner

tests_dir: str = os.path.dirname(__file__)
sw_dir: str = os.path.abspath(os.path.join(tests_dir, "..", "sw"))


def run_tests(
    ip: str, parameters: Dict[str, int], path: str, sim: str = "verilator"
) -> None:
    """Compile IP and run cocotb tests using runners."""

    rtl_dir: str = os.path.abspath(os.path.join(tests_dir, "..", "ips", path))
    sys.path.append(str(tests_dir))

    waves: bool = bool(os.getenv("ASPYCOT_WAVES", 0))

    dut: str = ip
    module: str = "testbench"
    toplevel: str = ip

    verilog_sources: List[str] = []

    # All IPs must define a file list to ease compile process
    with open(f"{rtl_dir}/Flist.{dut}") as flist:
        for f in flist:
            verilog_sources.append(os.path.join(rtl_dir, f))

    sim_build: str = os.path.join(tests_dir, f"{dut}_sim_build")

    runner: Simulator = get_runner(simulator_name=sim)

    runner.build(
        verilog_sources=verilog_sources,
        hdl_toplevel=toplevel,
        always=True,
        build_dir=sim_build,
        parameters=parameters,
        waves=waves,
    )

    runner.test(hdl_toplevel=toplevel, test_module=module, waves=waves)
