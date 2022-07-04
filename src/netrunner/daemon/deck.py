from __future__ import annotations

from underpants.engine import RulesEngine
from netrunner.engine.types import Decklist, DecklistRequest
from typing import Iterator
from netrunner.core import deck
from netrunner.db.cardpool import create_card
from netrunner.daemon.card import CardInfo


class Deck (deck.Deck):
    @staticmethod
    def list_decks(engine: RulesEngine, url: str) -> Decklist:
        return engine.request(Decklist, DecklistRequest(url))

    @classmethod
    def iter_decks(cls, decklist: Decklist) -> Iterator[Deck]:
        for deck in decklist.data:
            yield cls.create(
                id=deck["uuid"],
                name=deck["name"],
                cards=tuple((count, create_card(code=card_code)) for card_code, count in deck["cards"].items()),
            )

    def serialize(self):
        return dict(
            id=self.id,
            name=self.name,
            cards=[dict(card=CardInfo.serialize(card=card), count=count) for count, card in self.cards],
        )
