from enum import Flag, auto


class ThreatModel(Flag):
    LEGIT = auto()
    ROP = auto()
    JOP = auto()
    ADG = auto()


def get_model(model: str) -> ThreatModel:
    return {
        "Legit": ThreatModel.LEGIT,
        "ROP": ThreatModel.ROP,
        "JOP": ThreatModel.JOP,
        "ADG": ThreatModel.ADG,
    }[model]
