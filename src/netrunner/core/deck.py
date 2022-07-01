from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from netrunner.core.card import Card, IdentityCard


@dataclass(frozen=True)
class Deck:
    identity: IdentityCard
    cards: tuple[Card, ...]
    additional: tuple[Card, ...] = ()

    @property
    def is_legal(self) -> bool:
        return len(list(self.check_deck())) == 0

    def check_deck(self) -> Iterator[str]:
        """Returns any issues found with the deck."""
        num_cards = len(self.cards)
        min_cards = self.identity.minimum_deck_size
        if num_cards < min_cards:
            yield f"Too few cards in deck. {num_cards} is less than {min_cards}."
