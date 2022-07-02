from __future__ import annotations

from enum import Enum
from typing import Union


class RunnerFaction(Enum):
    Anarch = "anarch"
    Criminal = "criminal"
    Shaper = "shaper"
    Adam = "adam"
    Apex = "apex"
    Sunny_Lebeau = "sunny-lebeau"


class CorpFaction(Enum):
    Haas_Bioroid = "haas-bioriod"
    Jinteki = "jinteki"
    NBN = "nbn"
    Weyland = "weyland-consortium"


Faction = Union[CorpFaction, RunnerFaction]
