from __future__ import annotations

from netrunner.core.card import IdentityCard
from netrunner.core.deck import Deck
from netrunner.db.cardpool import create_card


def test_deck_attributes() -> None:
    deck = Deck(
        id="123",
        name="test deck",
        identity=create_card(code="01093", card_type=IdentityCard),
        cards=(),
    )
    assert not deck.is_legal
