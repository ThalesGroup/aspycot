from abc import ABC, abstractmethod
from typing import Dict, Optional, Type

import cocotb
from arch import Instruction
from models import ThreatModel
from cocotb.triggers import RisingEdge, Timer


class Wrapper(ABC):
    def __init__(self, dut) -> None:
        self.dut = dut
        self.detects: Optional[ThreatModel] = None

    @abstractmethod
    async def init(self) -> None:
        pass

    @abstractmethod
    async def reset_toggle(self) -> None:
        pass

    @abstractmethod
    async def execute_instr(self, instr: Instruction) -> None:
        pass

    @abstractmethod
    async def raised_exception(self) -> bool:
        pass

    def can_detect(self, model: ThreatModel) -> bool:
        pass


class JOPAlarm(Wrapper):
    def __init__(self, dut) -> None:
        super().__init__(dut)

        self.detects = ThreatModel.JOP

        if cocotb.simulator.is_running():
            self.JopThreshold = int(cocotb.top.JopThreshold)
            self.StepUpValue = int(cocotb.top.StepUpValue)
            self.StepDownValue = int(cocotb.top.StepDownValue)

    async def init(self) -> None:
        """Initialize input signals value"""

        self.dut.instr_valid_i.value = 0
        self.dut.is_ind_jump_i.value = 0

        self.dut.rst_ni.value = 0

        await Timer(1, units="ns")

    async def reset_toggle(self) -> None:
        """Toggle reset signal"""

        # Turn off reset
        self.dut.rst_ni.value = 1

        await Timer(35, units="ns")

        assert self.dut.rst_ni.value == 1, f"{self.dut.name} is still under reset"

    async def execute_instr(self, instr: Instruction) -> None:
        """Initialize input signals value"""

        self.dut.instr_valid_i.value = 1
        self.dut.is_ind_jump_i.value = instr.is_jr()

        await RisingEdge(self.dut.clk_i)

    async def raised_exception(self) -> bool:
        return self.dut.alarm_o.value == 1

    def can_detect(self, model: ThreatModel) -> bool:
        return self.detects == model


def wrap(dut) -> Wrapper:
    """Wrap dut with abstract class"""
    supported_ips: Dict[str, Type[Wrapper]] = {
        "jop_alarm": JOPAlarm,
    }
    ip: str = dut._name
    try:
        return supported_ips[ip](dut)
    except KeyError:
        raise ValueError(
            f"IP {ip!r} is not in supported IPs: {', '.join(supported_ips.keys())}"
        ) from None
