from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import islice
from typing import Iterable, Iterator

from netrunner.core.card import Card
from netrunner.core.error import OutOfCardsError
from netrunner.core.zone import GameZone


@dataclass(frozen=True)
class CardState:
    card: Card
    zone: GameZone = GameZone.deck
    active: bool = False

    def draw(self) -> CardState:
        return replace(self, zone=GameZone.hand, active=False)


@dataclass(frozen=True)
class Cards:
    all_cards: tuple[CardState, ...] = ()

    @classmethod
    def init(cls, cards: Iterable[Card]) -> Cards:
        return cls(tuple(map(CardState, cards)))

    def draw(
        self, count: int, from_zone: GameZone = GameZone.deck, out_of_cards_error: bool = True
    ) -> Cards:
        deck = self.in_zone(from_zone)
        drawn = tuple(card_state.draw() for card_state in islice(deck, count))
        if out_of_cards_error and len(drawn) < count:
            raise OutOfCardsError(f"Could not draw {count} cards.")

        return replace(
            self,
            all_cards=(
                *drawn,
                *deck,
                *self.not_in_zone(from_zone),
            ),
        )

    def in_zone(self, zone: GameZone) -> Iterator[CardState]:
        yield from (state for state in self.all_cards if state.zone == zone)

    def not_in_zone(self, zone: GameZone) -> Iterator[CardState]:
        yield from (state for state in self.all_cards if state.zone != zone)
