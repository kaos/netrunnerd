"""Load all available cards to use.

Update `cardpool.json` from NetrunnerDB:

    $ curl https://netrunnerdb.com/api/2.0/public/cards | jq . > src/netrunner/db/cardpool.json
"""
from __future__ import annotations

import json
import logging
import pkgutil
from collections import defaultdict
from typing import Any, Dict, TypeVar, overload

from netrunner.core.card import Card, CorpCard, RunnerCard, get_card_type
from netrunner.core.error import GameError
from netrunner.core.faction import get_faction


class DBError(GameError):
    """DB Error."""


CardData = Dict[str, Any]
_data: dict[str, Any] = {}
logger = logging.getLogger(__name__)


def _get_cardpool() -> dict:
    if not _data:
        raw = pkgutil.get_data("netrunner.db", "cardpool.json")
        assert raw, "Failed to load cardpool.json from `netrunner.db`."
        _data.update(json.loads(raw.decode("utf-8")))
        logger.debug(
            f"Loaded cardpool {_data['version_number']} with {_data['total']} cards "
            f"updated {_data['last_updated']}."
        )
    return _data


def get_card_data(*, code: str | None = None, name: str | None = None) -> CardData:
    if code is None:
        assert name, "Must provide `code` or `name` to `netrunner.db.cardpool.find_card()`."
        key = "stripped_title"
        value = name
    else:
        assert (
            name is None
        ), "Must not provide both `code` and `name` to `netrunner.db.cardpool.find_card()`."
        key = "code"
        value = code

    for card in _get_cardpool()["data"]:
        if value == card[key]:
            return card

    raise DBError(f"Unknown card {key}: {value!r}.")


CardT = TypeVar("CardT", bound=Card)


@overload
def create_card(
    *, code: str | None = None, name: str | None = None, card_type: type[CardT]
) -> CardT:
    ...


@overload
def create_card(*, code: str | None = None, name: str | None = None) -> Card:
    ...


def create_card(*, code: str | None = None, name: str | None = None, card_type=Card):
    data = get_card_data(code=code, name=name)
    card_type_enum = get_card_type(data["side_code"], data["type_code"])
    card = Card.create(card_type_enum, **_card_factory[card_type_enum](data))
    if not isinstance(card, card_type):
        raise DBError(
            f"Expected to create a {card_type} for {code or name!r}, but got {type(card)}"
        )
    return card


def _unknown_card(data) -> CardData:
    raise DBError(f"No card factory for {data['side_code']} {data['type_code']}.")


def _base_card_factory(data: CardData) -> CardData:
    return dict(
        faction=get_faction(data["side_code"], data["faction_code"]),
        name=data["stripped_title"],
        influence=data.get("faction_cost"),
    )


def _identity_card_factory(data: CardData) -> CardData:
    return dict(
        minimum_deck_size=data["minimum_deck_size"],
        influence_limit=data["influence_limit"],
        **_base_card_factory(data),
    )


def _playable_card_factory(data: CardData) -> CardData:
    return {}


_card_factory = defaultdict(
    lambda: _unknown_card,
    {
        CorpCard.identity: _identity_card_factory,
        CorpCard.agenda: _playable_card_factory,
        RunnerCard.identity: _identity_card_factory,
    },
)
