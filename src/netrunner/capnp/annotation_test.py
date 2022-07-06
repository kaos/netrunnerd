from __future__ import annotations

from netrunner.db.cardpool import create_card

from netrunner.capnp.annotation import CapAn


def test_create_card() -> None:
    card = create_card(code="01093")
    data = CapAn.serialize_dataclass(card)
    assert 36 == len(data["id"])
    assert data == dict(
        id=data["id"],  # Random value.
        code="01093",
        influence=0,
        name="Weyland Consortium: Building a Better World",
        title="Weyland Consortium: Building a Better World",
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
