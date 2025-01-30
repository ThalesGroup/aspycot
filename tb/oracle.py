import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Type

from models import ThreatModel, get_model
from runner import sw_dir
from wrappers import Wrapper


def read_json() -> Dict[str, List[str]]:
    file: str = os.path.abspath(os.path.join(sw_dir, "applications.json"))

    with open(file, "r") as f:
        return json.load(f)


class Oracle(ABC):
    classification: Dict[str, str] = read_json()

    def __init__(self, app: str) -> None:
        self.app: str = app
        self.model: ThreatModel = get_model(Oracle.classification[app])
        self.early_exit: bool = False

    @abstractmethod
    async def check_exit_condition(self, wrapper: Wrapper) -> bool:
        pass

    @abstractmethod
    def decision(self, wrapper: Wrapper) -> None:
        pass


class CFI(Oracle):
    def __init__(self, app) -> None:
        super().__init__(app)

    async def check_exit_condition(self, wrapper: Wrapper) -> bool:
        if await wrapper.raised_exception():
            self.early_exit = True
            return True

        return False

    def decision(self, wrapper: Wrapper):
        # Depending on the type of applications, execeptions can be expected or not
        if self.early_exit and self.model == ThreatModel.LEGIT:
            assert (
                False
            ), f"False positive: execution of {self.app} led to an exception."

        if (
            self.model != ThreatModel.LEGIT
            and not self.early_exit
            and wrapper.can_detect(self.model)
        ):
            assert (
                False
            ), f"False negative: execution of {self.app} raised no exception."


def get_oracle(dut, app: str) -> Oracle:
    """Build oracle depending on the IP"""

    supported_ips: Dict[str, Type[Oracle]] = {
        "jop_alarm": CFI,
    }
    ip: str = dut._name
    try:
        return supported_ips[ip](app)
    except KeyError:
        raise ValueError(
            f"IP {ip!r} is not in supported IPs: {', '.join(supported_ips.keys())}"
        ) from None
