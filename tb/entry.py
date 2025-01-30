from typing import Dict

import pytest
from runner import run_tests

"""Main entry point of the testbench.

This file contains the declaration of the tests read by pytest following this format:

>>> test_${IP}_ip(*args)

For each IP, a set of parameters can be defined.
"""


@pytest.mark.parametrize("JopThreshold", [100, 120])
@pytest.mark.parametrize("StepUpValue", [10, 20])
@pytest.mark.parametrize("StepDownValue", [1, 4])
def test_jop_alarm_ip(JopThreshold, StepUpValue, StepDownValue):
    """jop_alarm IP entry point"""

    parameters: Dict[str, str] = {
        "JopThreshold": JopThreshold,
        "StepUpValue": StepUpValue,
        "StepDownValue": StepDownValue,
    }

    run_tests("jop_alarm", parameters, "jop_alarm/hw/", sim="verilator")
