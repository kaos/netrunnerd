from __future__ import annotations

from typing import Union, cast

from netrunner.util import EnumUnion

from netrunner.core.enum import CorpEnum, RunnerEnum


class RunnerFaction(RunnerEnum):
    Anarch = "anarch"
    Criminal = "criminal"
    Shaper = "shaper"
    Adam = "adam"
    Apex = "apex"
    Sunny_Lebeau = "sunny-lebeau"
    Neutral = "neutral-runner"


class CorpFaction(CorpEnum):
    Haas_Bioroid = "haas-bioriod"
    Jinteki = "jinteki"
    NBN = "nbn"
    Weyland = "weyland-consortium"
    Neutral = "neutral-corp"


Faction = Union[CorpFaction, RunnerFaction]


def get_faction(side: str, value: str) -> Faction:
    return cast(Faction, EnumUnion.find_value(Faction, value, side=side))


def serialize_faction(faction: Faction) -> dict:
    return dict(
        name=faction.value,
        side=faction._get_side(),
    )
