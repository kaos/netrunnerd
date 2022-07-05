from __future__ import annotations

from netrunner.core.card import CorpCard, CorpIdentityCard
from netrunner.core.faction import CorpFaction
from netrunner.db.cardpool import _get_cardpool, create_card, get_card_data


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


def test_common_card_fields() -> None:
    """Check which fields that all cards have, and which are for speicific per
    card type."""
    cards = iter(_get_cardpool()["data"])
    all_fields = {}

    def update_fields(card_type, fields):
        if card_type not in all_fields:
            all_fields[card_type] = set(fields)
        else:
            all_fields[card_type].intersection_update(fields)

    for card in cards:
        assert isinstance(card.get("faction_cost"), int)

        fields = set(card.keys())
        for card_type in ("_common", card["type_code"]):
            update_fields(card_type, fields)

    for card_type, fields in all_fields.items():
        if card_type != "_common":
            fields.difference_update(all_fields["_common"])

    assert {
        "_common": {
            "code",
            "deck_limit",
            "faction_code",
            "faction_cost",
            "pack_code",
            "position",
            "quantity",
            "side_code",
            "stripped_title",
            "title",
            "type_code",
            "uniqueness",
        },
        "agenda": {
            "advancement_cost",
            "agenda_points",
            "illustrator",
        },
        "asset": {
            "cost",
            "illustrator",
            "stripped_text",
            "text",
            "trash_cost",
        },
        "event": {
            "cost",
            "illustrator",
            "stripped_text",
            "text",
        },
        "hardware": {
            "cost",
            "illustrator",
            "stripped_text",
            "text",
        },
        "ice": {
            "cost",
            "illustrator",
            "keywords",
            "strength",
            "stripped_text",
            "text",
        },
        "identity": {
            "influence_limit",
            "keywords",
            "minimum_deck_size",
        },
        "operation": {
            "cost",
            "illustrator",
            "stripped_text",
            "text",
        },
        "program": {
            "cost",
            "memory_cost",
            "stripped_text",
            "text",
        },
        "resource": {
            "cost",
            "stripped_text",
            "text",
        },
        "upgrade": {
            "cost",
            "illustrator",
            "stripped_text",
            "text",
            "trash_cost",
        },
    } == all_fields
