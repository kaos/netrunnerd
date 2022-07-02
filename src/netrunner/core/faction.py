from __future__ import annotations

from typing import Union, cast

from netrunner.core.enum import CorpEnum, RunnerEnum
from netrunner.util import EnumUnion


class RunnerFaction(RunnerEnum):
    Anarch = "anarch"
    Criminal = "criminal"
    Shaper = "shaper"
    Adam = "adam"
    Apex = "apex"
    Sunny_Lebeau = "sunny-lebeau"


class CorpFaction(CorpEnum):
    Haas_Bioroid = "haas-bioriod"
    Jinteki = "jinteki"
    NBN = "nbn"
    Weyland = "weyland-consortium"


Faction = Union[CorpFaction, RunnerFaction]


def get_faction(side: str, value: str) -> Faction:
    return cast(Faction, EnumUnion.find_value(Faction, value, side=side))
