from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Literal, Union, cast

from netrunner.core.enum import CorpEnum, RunnerEnum
from netrunner.core.faction import Faction
from netrunner.util import EnumUnion


class CorpCard(CorpEnum):
    identity = "identity"
    agenda = "agenda"
    asset = "asset"
    ice = "ice"
    operation = "operation"
    upgrade = "upgrade"


class RunnerCard(RunnerEnum):
    identity = "identity"
    event = "event"
    hardware = "hardware"
    program = "program"
    resource = "resource"


CardType = Union[CorpCard, RunnerCard]


def get_card_type(side: str, value: str) -> CardType:
    return cast(CardType, EnumUnion.find_value(CardType, value, side=side))


@dataclass(frozen=True)
class Card:
    type: ClassVar[CardType]

    faction: Faction
    name: str
    influence: Literal[0, 1, 2, 3, 4, 5] | None

    @staticmethod
    def create(card_type: CardType, **kwargs) -> Card:
        for cls in Card.__subtypes():
            if cls.type is card_type:
                return cls(**kwargs)
        raise NotImplementedError(f"No `Card` implementation for {card_type}.")

    @classmethod
    def __subtypes(cls):
        for sub in cls.__subclasses__():
            if hasattr(sub, "type"):
                yield sub
            else:
                yield from sub.__subtypes()


@dataclass(frozen=True)
class IdentityCard(Card):
    minimum_deck_size: int
    influence_limit: int


@dataclass(frozen=True)
class CorpIdentityCard(IdentityCard):
    type = CorpCard.identity


@dataclass(frozen=True)
class RunnerIdentityCard(IdentityCard):
    type = RunnerCard.identity
