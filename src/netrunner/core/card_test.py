from __future__ import annotations

from netrunner.core.card import Card, CorpCard, CorpIdentityCard
from netrunner.core.faction import CorpFaction


def test_create_card() -> None:
    card = Card.get_card_cls(CorpCard.identity)(  # type: ignore[call-arg]
        faction=CorpFaction.Weyland,
        id="123",
        code="456",
        name="Test",
        influence=0,
        minimum_deck_size=5,
        influence_limit=10,
        unique=False,
        deck_limit=1,
    )
    assert isinstance(card, CorpIdentityCard)
    assert card.name == "Test"
    assert card.faction == CorpFaction.Weyland
