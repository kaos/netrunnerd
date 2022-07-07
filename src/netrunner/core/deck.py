from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from typing import Annotated, Iterator, Sequence, TypeVar, overload

from netrunner.annotations import NDB
from netrunner.core.card import Card, IdentityCard
from netrunner.core.error import DeckCardLimitError, DeckError, DeckInfluenceOverspentError

T = TypeVar("T")


@dataclass(frozen=True)
class DeckCard:
    count: int
    card: Card

    def get_cards(self) -> tuple[Card, ...]:
        return self.count * (self.card,)


@dataclass(frozen=True)
class Deck:
    id: Annotated[str, NDB("uuid")]
    name: str
    identity: IdentityCard
    cards: tuple[DeckCard, ...]

    @classmethod
    def create(cls, cards: Sequence[tuple[int, Card]], **kwargs) -> Deck:
        return cls(
            identity=next(card for _, card in cards if isinstance(card, IdentityCard)),
            cards=tuple(
                DeckCard(n, card) for n, card in cards if not isinstance(card, IdentityCard)
            ),
            **kwargs,
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

        influence_limit = self.identity.influence_limit
        influence_used = sum(
            deck_card.count * deck_card.card.influence
            for deck_card in self.cards
            if deck_card.card.faction != self.identity.faction
        )
        if influence_used > influence_limit:
            yield DeckInfluenceOverspentError(influence_limit, influence_used)

    @overload
    def shuffle(self, cards: Sequence[T]) -> Iterator[T]:
        ...

    @overload
    def shuffle(self) -> Iterator[Card]:
        ...

    def shuffle(self, cards=None) -> Iterator:
        if cards is None:
            cards = itertools.chain.from_iterable(map(DeckCard.get_cards, self.cards))
        items = list(cards)
        random.shuffle(items)
        yield from items
