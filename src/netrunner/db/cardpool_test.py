from __future__ import annotations

from netrunner.core.card import CorpCard, CorpIdentityCard
from netrunner.core.faction import CorpFaction
from netrunner.db.cardpool import create_card, get_card_data


def test_get_card_data() -> None:
    data = get_card_data(code="01093")
    assert data
    assert data["title"] == "Weyland Consortium: Building a Better World"


def test_create_card() -> None:
    card = create_card(code="01093")
    assert isinstance(card, CorpIdentityCard)
    assert card.type == CorpCard.identity
    assert card.minimum_deck_size == 45
    assert card.influence_limit == 15
    assert card.faction == CorpFaction.Weyland
    assert card.name == "Weyland Consortium: Building a Better World"
    assert card.influence == 0
