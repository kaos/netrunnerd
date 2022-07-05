"""Load all available cards to use.

Update `cardpool.json` from NetrunnerDB:

    $ curl https://netrunnerdb.com/api/2.0/public/cards | jq . > src/netrunner/db/cardpool.json
"""
from __future__ import annotations

import json
import logging
import pkgutil
from typing import Any, Dict, TypeVar, cast, overload

from netrunner.core.card import Card
from netrunner.core.error import GameError


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
            return cast(CardData, card)

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


def create_card(*, code=None, name=None, card_type=Card):
    data = get_card_data(code=code, name=name)
    card = Card.from_netrunner_db_card(data)
    if not isinstance(card, card_type):
        raise DBError(
            f"Expected to create a {card_type} for {code or name!r}, but got {type(card)}"
        )
    return card
