from parser import get_app_instr, get_apps_path
from typing import List

import cocotb
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.triggers import ClockCycles
from oracle import Oracle, get_oracle
from wrappers import Wrapper, wrap


async def run_app(dut, app: str) -> None:
    """Run trace of an application on hardware IP"""

    # Retrieve corresponding trace
    path: str = apps[app]

    # Wrap dut in abstract class to retrieve its specific functions
    wrapper: Wrapper = wrap(dut)
    oracle: Oracle = get_oracle(dut, app)

    await wrapper.init()
    await wrapper.reset_toggle()

    # Start clock
    cocotb.start_soon(Clock(dut.clk_i, period=10, units="ns").start())

    await ClockCycles(dut.clk_i, 5)

    # Parse trace and execute instructions
    for instr, cycle in get_app_instr(path):
        await wrapper.execute_instr(instr)

        # Monitor IP exception signals
        if await oracle.check_exit_condition(wrapper):
            dut._log.info(f"Ending test at instruction: {instr}")
            break

    dut._log.info(f"Processed instruction count : {cycle}") if cycle else ()
    oracle.decision(wrapper)


global apps
apps: List[str] = get_apps_path()

# Factory of tests to run all requested applications
factory: TestFactory = TestFactory(run_app)

factory.add_option(name="app", optionlist=apps.keys())
factory.generate_tests()
