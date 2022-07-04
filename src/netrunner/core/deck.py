from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterator, Sequence, TypeVar, overload
import itertools
from netrunner.core.card import Card, IdentityCard
from netrunner.core.error import GameError

T = TypeVar("T")


class DeckError(GameError):
    """Deck error base class."""


class DeckCardLimitError(DeckError):
    """Deck has not enough cards."""

    def __init__(self, num_cards: int, min_cards: int) -> None:
        self.num_cards = num_cards
        self.min_cards = min_cards
        super().__init__(f"{num_cards} is less than {min_cards}.")


@dataclass(frozen=True)
class Deck:
    id: str
    name: str
    identity: IdentityCard
    cards: tuple[tuple[int, Card], ...]

    @classmethod
    def create(cls, cards: Sequence[tuple[int, Card]], **kwargs) -> Deck:
        return cls(
            identity=next(card for _, card in cards if isinstance(card, IdentityCard)),
            cards=tuple((n, card) for n, card in cards if not isinstance(card, IdentityCard)),
            **kwargs
        )

    @property
    def is_legal(self) -> bool:
        return len(list(self.check())) == 0

    def check(self) -> Iterator[DeckError]:
        """Returns any issues found with the deck."""
        num_cards = len(self.cards)
        min_cards = self.identity.minimum_deck_size
        if num_cards < min_cards:
            yield DeckCardLimitError(num_cards, min_cards)

    @overload
    def shuffle(self, cards: Sequence[T]) -> Iterator[T]:
        ...

    @overload
    def shuffle(self) -> Iterator[Card]:
        ...

    def shuffle(self, cards=None) -> Iterator:
        if cards is None:
            cards = itertools.chain.from_iterable(n * [card] for n, card in self.cards)
        items = list(cards)
        random.shuffle(items)
        yield from items
