from __future__ import annotations

from netrunner.core.card import Card, CorpIdentityCard
from netrunner.core.faction import CorpFaction


def test_create_card() -> None:
    card = Card.from_code("01093")
    assert isinstance(card, CorpIdentityCard)
    assert card.name == "Weyland Consortium: Building a Better World"
    assert card.faction == CorpFaction.Weyland
