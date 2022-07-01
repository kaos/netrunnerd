from __future__ import annotations

from enum import Enum
from typing import Union


class RunnerFaction(Enum):
    Anarch = "anarch"
    Criminal = "criminal"
    Shaper = "shaper"


class CorpFaction(Enum):
    Haas_Bioroid = "haas-bioriod"
    Jinteki = "jinteki"
    NBN = "nbn"
    Weyland = "weyland-consortium"


Faction = Union[CorpFaction, RunnerFaction]
