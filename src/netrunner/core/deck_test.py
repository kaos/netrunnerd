from __future__ import annotations

from netrunner.core.card import IdentityCard
from netrunner.core.deck import Deck


def test_deck_attributes() -> None:
    deck = Deck(identity=IdentityCard.from_code("01093"), cards=())
    assert not deck.is_legal
