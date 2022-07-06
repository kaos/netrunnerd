from __future__ import annotations

from typing import Iterator

from underpants.engine import RulesEngine

from netrunner.core.deck import Deck
from netrunner.daemon.card import CardInfo
from netrunner.db.cardpool import create_card
from netrunner.engine.types import Decklist, DecklistRequest


class DeckInfo:
    @staticmethod
    def list_decks(engine: RulesEngine, url: str) -> Decklist:
        return engine.request(Decklist, DecklistRequest(url))

    @classmethod
    def iter_decks(cls, decklist: Decklist) -> Iterator[Deck]:
        for d in decklist.data:
            yield Deck.create(
                id=d["uuid"],
                name=d["name"],
                cards=tuple(
                    (count, create_card(code=card_code)) for card_code, count in d["cards"].items()
                ),
            )

    @staticmethod
    def serialize(deck: Deck):
        return dict(
            id=deck.id,
            name=deck.name,
            identity=CardInfo.serialize(card=deck.identity),
            cards=[
                dict(card=CardInfo.serialize(card=card), count=count) for count, card in deck.cards
            ],
        )
