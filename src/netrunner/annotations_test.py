from __future__ import annotations

from itertools import count
from pprint import pformat
from uuid import uuid4, uuid5

import pytest

from netrunner import api
from netrunner.annotations import CapAn
from netrunner.core.deck import Deck
from netrunner.db.cardpool import _get_cardpool, create_card


def test_serialize_card() -> None:
    card = create_card(code="01093")
    data = CapAn.serialize_dataclass(card)
    assert 36 == len(data["id"])
    assert data == dict(
        id=data["id"],  # Random value.
        code="01093",
        influence=0,
        name="Weyland Consortium: Building a Better World",
        unique=False,
        deckLimit=1,
        faction=dict(
            name="weyland-consortium",
            side="corp",
        ),
        identity=dict(
            influenceLimit=15,
            minimumDeckSize=45,
        ),
    )


def test_serialize_deck(monkeypatch) -> None:
    ns = uuid4()
    counter = count()
    monkeypatch.setattr("netrunner.core.card.uuid4", lambda: uuid5(ns, str(next(counter))))

    cards = {
        "10043": 2,
        "22015": 1,
        "31037": 3,
    }
    deck = Deck.create(
        id="be5f934b-2850-4fea-9ba3-f04848aa74dc",
        name="How To Build A Runner Deck - Akiko Nisei",
        cards=[(count, create_card(code=code)) for code, count in cards.items()],
    )
    data = CapAn.serialize_dataclass(deck)
    assert data == dict(
        id="be5f934b-2850-4fea-9ba3-f04848aa74dc",
        name="How To Build A Runner Deck - Akiko Nisei",
        identity=dict(
            id=str(uuid5(ns, "1")),
            code="22015",
            faction=dict(side="runner", name="shaper"),
            name="Akiko Nisei: Head Case",
            influence=0,
            unique=False,
            deckLimit=1,
            identity=dict(
                minimumDeckSize=45,
                influenceLimit=12,
            ),
        ),
        cards=(
            dict(
                count=2,
                card=dict(
                    id=str(uuid5(ns, "0")),
                    code="10043",
                    faction=dict(side="runner", name="criminal"),
                    name="Political Operative",
                    influence=1,
                    unique=False,
                    deckLimit=3,
                    resource=dict(
                        cost=1,
                        strippedText=(
                            "Install only if you made a successful run on HQ this turn. "
                            "trash, X credits: Trash 1 rezzed card with trash cost equal to X."
                        ),
                        text=(
                            "Install only if you made a successful run on HQ this turn.\n"
                            "<strong>[trash]</strong>, <strong>X[credit]:</strong> "
                            "Trash 1 rezzed card with trash cost equal to X."
                        ),
                    ),
                ),
            ),
            dict(
                count=3,
                card=dict(
                    id=str(uuid5(ns, "2")),
                    code="31037",
                    faction=dict(side="runner", name="neutral-runner"),
                    name="Dirty Laundry",
                    influence=0,
                    unique=False,
                    deckLimit=3,
                    event=dict(
                        cost=2,
                        strippedText=(
                            "Run any server. When that run ends, "
                            "if it was successful, gain 5 credits."
                        ),
                        text=(
                            "Run any server. When that run ends, "
                            "if it was successful, gain 5[credit]."
                        ),
                    ),
                ),
            ),
        ),
    )

    print(f"Serialized deck:\n{pformat(data)}\n")
    capnp_deck = api.Deck.new_message(**data)
    assert capnp_deck.id == "be5f934b-2850-4fea-9ba3-f04848aa74dc"


@pytest.mark.parametrize("card_code", [data["code"] for data in _get_cardpool()["data"]])
def test_serialize_all_cards_to_capnp(card_code: str) -> None:
    card = create_card(code=card_code)
    print(f"CARD:\n{card}\n")

    serialized = CapAn.serialize_dataclass(card)
    print(f"Serialized:\n{pformat(serialized)}\n")

    capnp_card = api.Card.new_message(**serialized)
    print(f"CAPNP Card:\n{capnp_card}\n")

    assert capnp_card.name == card.name
