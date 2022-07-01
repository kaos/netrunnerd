from __future__ import annotations

from netrunner.db.cardpool import find_card_data


def test_find_card_data() -> None:
    card = find_card_data(code="01093")
    assert card
    assert card["title"] == "Weyland Consortium: Building a Better World"
