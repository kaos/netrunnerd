from __future__ import annotations

from dataclasses import dataclass, fields
from functools import partial
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Iterator,
    Literal,
    Type,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)
from uuid import uuid4

from netrunner.capnp.annotation import CapAn
from netrunner.core.enum import CorpEnum, RunnerEnum
from netrunner.core.faction import Faction, get_faction, serialize_faction
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


class NDB:
    """Map netrunner.core.card field to a NetrunnerDB card field."""

    field_names: tuple[str, ...]
    convert: Callable | None

    def __init__(self, *field_name: str, convert: Callable | None = None, skip: bool = False):
        if len(field_name) > 1:
            assert convert

        self.field_names = field_name
        self.convert = convert

    def field_value(self, field_name: str, data: dict[str, Any]) -> Any:
        values = (data.get(field) for field in self.field_names or (field_name,))
        if self.convert:
            return self.convert(*values)
        else:
            return next(values)

    @classmethod
    def field_values_for(cls, card_type: type[Card], data: dict[str, Any]) -> dict[str, Any]:
        field_values = {}
        field_types = get_type_hints(card_type, include_extras=True)
        for field in fields(card_type):
            field_values[field.name] = cls.get_value_for_type(
                field_types[field.name], field.name, data
            )
        return field_values

    @classmethod
    def get_value_for_type(cls, field_type: Any, field_name: str, data: dict[str, Any]) -> Any:
        if get_origin(field_type) is Annotated:
            for arg in get_args(field_type):
                if isinstance(arg, cls):
                    return arg.field_value(field_name, data)
        return data.get(field_name)


@dataclass(frozen=True)
class Card:
    _ndb_type: ClassVar[NDB] = NDB("side_code", "type_code", convert=get_card_type)
    type: ClassVar[CardType]

    id: Annotated[str, NDB("code", convert=lambda _: str(uuid4()))]
    code: str
    faction: Annotated[
        Faction,
        NDB("side_code", "faction_code", convert=get_faction),
        CapAn(convert=serialize_faction),
    ]
    name: Annotated[str, NDB("stripped_title")]
    influence: Annotated[Literal[0, 1, 2, 3, 4, 5], NDB("faction_cost")]
    unique: Annotated[bool, NDB("uniqueness")]
    deck_limit: int

    @classmethod
    def from_netrunner_db_card(cls, data: dict[str, Any]) -> Card:
        card_type = cls._ndb_type.field_value("type", data)
        card_cls = cls.get_card_cls(card_type)
        return card_cls(**NDB.field_values_for(card_cls, data))

    @classmethod
    def get_card_cls(cls, card_type: CardType) -> Type[Card]:
        for card_cls in cls.__subtypes():
            if card_cls.type is card_type:
                return card_cls
        raise TypeError(f"No implementation in netrunner.core.card for card type: {card_type}")

    @classmethod
    def __subtypes(cls) -> Iterator[Type[Card]]:
        for sub in cls.__subclasses__():
            if hasattr(sub, "type"):
                yield sub
            else:
                yield from sub.__subtypes()


CapAgenda = partial(CapAn, group="agenda")
CapAsset = partial(CapAn, group="asset")
CapEvent = partial(CapAn, group="event")
CapHardware = partial(CapAn, group="hardware")
CapIce = partial(CapAn, group="ice")
CapIdentity = partial(CapAn, group="identity")
CapOperation = partial(CapAn, group="operation")
CapProgram = partial(CapAn, group="program")
CapResource = partial(CapAn, group="resource")
CapUpgrade = partial(CapAn, group="upgrade")


@dataclass(frozen=True)
class IdentityCard(Card):
    minimum_deck_size: Annotated[int, CapIdentity()]
    influence_limit: Annotated[int, CapIdentity()]


@dataclass(frozen=True)
class CorpIdentityCard(IdentityCard):
    type = CorpCard.identity


@dataclass(frozen=True)
class RunnerIdentityCard(IdentityCard):
    type = RunnerCard.identity


@dataclass(frozen=True)
class AgendaCard(Card):
    type = CorpCard.agenda
    advancement_cost: Annotated[int, CapAgenda()]
    agenda_points: Annotated[int, CapAgenda()]


@dataclass(frozen=True)
class AssetCard(Card):
    type = CorpCard.asset
    cost: Annotated[int, CapAsset()]
    stripped_text: Annotated[str, CapAsset()]
    text: Annotated[str, CapAsset()]
    trash_cost: Annotated[int, CapAsset()]


@dataclass(frozen=True)
class IceCard(Card):
    type = CorpCard.ice
    cost: Annotated[int, CapIce()]
    keywords: Annotated[str, CapIce()]
    strength: Annotated[int, CapIce()]
    stripped_text: Annotated[str, CapIce()]
    text: Annotated[str, CapIce()]


@dataclass(frozen=True)
class OperationCard(Card):
    type = CorpCard.operation
    cost: Annotated[int, CapOperation()]
    stripped_text: Annotated[str, CapOperation()]
    text: Annotated[str, CapOperation()]


@dataclass(frozen=True)
class UpgradeCard(Card):
    type = CorpCard.upgrade
    cost: Annotated[int, CapUpgrade()]
    stripped_text: Annotated[str, CapUpgrade()]
    text: Annotated[str, CapUpgrade()]
    trash_cost: Annotated[int, CapUpgrade()]


@dataclass(frozen=True)
class EventCard(Card):
    type = RunnerCard.event
    cost: Annotated[int, CapEvent()]
    stripped_text: Annotated[str, CapEvent()]
    text: Annotated[str, CapEvent()]


@dataclass(frozen=True)
class HardwareCard(Card):
    type = RunnerCard.hardware
    cost: Annotated[int, CapHardware()]
    stripped_text: Annotated[str, CapHardware()]
    text: Annotated[str, CapHardware()]


@dataclass(frozen=True)
class ProgramCard(Card):
    type = RunnerCard.program
    cost: Annotated[int, CapProgram()]
    memory_cost: Annotated[int, CapProgram()]
    stripped_text: Annotated[str, CapProgram()]
    text: Annotated[str, CapProgram()]


@dataclass(frozen=True)
class ResourceCard(Card):
    type = RunnerCard.resource
    cost: Annotated[int, CapResource()]
    stripped_text: Annotated[str, CapResource()]
    text: Annotated[str, CapResource()]
