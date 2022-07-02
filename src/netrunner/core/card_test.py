from __future__ import annotations

from netrunner.core.card import Card, CorpCard, CorpIdentityCard
from netrunner.core.faction import CorpFaction


def test_create_card() -> None:
    card = Card.create(
        CorpCard.identity,
        faction=CorpFaction.Weyland,
        name="Test",
        influence=None,
        minimum_deck_size=5,
        influence_limit=10,
    )
    assert isinstance(card, CorpIdentityCard)
    assert card.name == "Test"
    assert card.faction == CorpFaction.Weyland
