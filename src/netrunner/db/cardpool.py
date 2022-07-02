"""Load all available cards to use.

Update `cardpool.json` from NetrunnerDB:

    $ curl https://netrunnerdb.com/api/2.0/public/cards | jq . > src/netrunner/db/cardpool.json
"""
from __future__ import annotations

import json
import logging
import pkgutil
from typing import Any, Dict

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


def find_card_data(*, code: str | None = None, name: str | None = None) -> CardData | None:
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

    return None
