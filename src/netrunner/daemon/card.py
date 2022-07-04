from __future__ import annotations

from typing import overload

from netrunner import api
from netrunner.core.card import Card
from netrunner.core.card_state import CardState


class CardInfo:
    @overload
    @staticmethod
    def serialize(*, card: Card) -> api.Card:
        ...

    @overload
    @staticmethod
    def serialize(*, state: CardState) -> api.Game.CardState:
        ...

    @staticmethod
    def serialize(*, card=None, state=None):
        if state:
            return dict(
                active=state.active,
                card=CardInfo.serialize(card=state.card),
                zone=state.zone.value,
            )
        else:
            return dict(name=card.name)
