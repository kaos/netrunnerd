from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Literal, Union, cast

from netrunner.core.faction import CorpFaction, Faction, RunnerFaction
from netrunner.db.cardpool import CardData, find_card_data


class CorpCard(Enum):
    identity = "identity"
    agenda = "agenda"
    asset = "asset"
    ice = "ice"
    operation = "operation"
    upgrade = "upgrade"


class RunnerCard(Enum):
    identity = "identity"
    event = "event"
    hardware = "hardware"
    program = "program"
    resource = "resource"


CardType = Union[CorpCard, RunnerCard]


@dataclass(frozen=True)
class Card:
    type: ClassVar[CardType]

    faction: Faction
    name: str
    influence: Literal[0, 1, 2, 3, 4, 5]

    @classmethod
    def from_card_data(cls, data: CardData, **kwargs) -> Card:
        kwargs.update(
            dict(
                faction=cls._get_faction(data["side_code"], data["faction_code"]),
                name=data["stripped_title"],
                influence=data.get("faction_cost", 0),
            )
        )
        return cls(**kwargs)

    @staticmethod
    def from_code(code: str) -> Card:
        data = find_card_data(code=code)
        assert data is not None, f"Unknown card code: {code!r}."
        return Card.create(data)

    @staticmethod
    def create(data: CardData) -> Card:
        card_type = Card._get_card_type(data["side_code"], data["type_code"])
        for cls in Card.__subtypes():
            if cls.type is card_type:
                return cls.from_card_data(data)
        raise NotImplementedError(f"No `Card` implementation for {card_type}.")

    @staticmethod
    def _get_card_type(side: str, card_type: str) -> CardType:
        types: type[CorpCard | RunnerCard]
        if side == "corp":
            types = CorpCard
        elif side == "runner":
            types = RunnerCard
        else:
            assert f"Unknown side code: {side!r}.e"

        for enum in types:
            if enum.value == card_type:
                return cast(CardType, enum)
        raise RuntimeError(f"Unknown {side} card type: {card_type!r}.")

    @staticmethod
    def _get_faction(side: str, faction: str) -> Faction:
        factions: type[CorpFaction | RunnerFaction]
        if side == "corp":
            factions = CorpFaction
        elif side == "runner":
            factions = RunnerFaction
        else:
            assert f"Unknown side code: {side!r}.e"

        for enum in factions:
            if enum.value == faction:
                return cast(Faction, enum)
        raise RuntimeError(f"Unknown {side} faction: {faction!r}.")

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

    @staticmethod
    def from_code(code: str) -> IdentityCard:
        card = Card.from_code(code)
        assert isinstance(
            card, IdentityCard
        ), f"Expected to load an identity card for code {code!r}, but got {card}."
        return card

    @classmethod
    def from_card_data(cls, data: CardData, **kwargs) -> Card:
        return super().from_card_data(
            data,
            minimum_deck_size=data["minimum_deck_size"],
            influence_limit=data["influence_limit"],
            **kwargs,
        )


@dataclass(frozen=True)
class CorpIdentityCard(IdentityCard):
    type = CorpCard.identity


@dataclass(frozen=True)
class RunnerIdentityCard(IdentityCard):
    type = RunnerCard.identity
