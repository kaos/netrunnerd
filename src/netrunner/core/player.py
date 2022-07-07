from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator

from netrunner.core.card_state import Cards
from netrunner.core.deck import Deck
from netrunner.core.error import GameError


class Role(Enum):
    corp = "Corp"
    runner = "Runner"


class PlayerError(GameError):
    def __init__(self, message: str, *, player: Player) -> None:
        super().__init__(f"{player.role.value}: {message}")
        self.player = player


@dataclass(frozen=True)
class Player:
    """The core data for a player."""

    role: Role
    deck: Deck | None = None
    cards: Cards = Cards()
    credit_pool: int = 0

    @classmethod
    def create(cls, deck: Deck | None = None) -> Player:
        raise NotImplementedError()

    @property
    def has_legal_deck(self) -> bool:
        if not self.deck:
            return False
        return self.deck.is_legal

    def check(self) -> Iterator[GameError]:
        if self.deck:
            yield from self.deck.check()
        else:
            yield PlayerError("missing deck", player=self)


@dataclass(frozen=True)
class Corp(Player):
    """The Corp role."""

    @classmethod
    def create(cls, deck: Deck | None = None) -> Player:
        return cls(deck=deck, role=Role.corp)

    # @property
    # def RnD(self) -> Iterator[CardState]:
    #     return self.cards.in_zone(GameZone.deck)

    # @property
    # def HQ(self) -> Iterator[CardState]:
    #     return self.cards.in_zone(GameZone.hand)

    # @property
    # def archives(self) -> Iterator[CardState]:
    #     return self.cards.in_zone(GameZone.discard)


@dataclass(frozen=True)
class Runner(Player):
    """The Runner role."""

    @classmethod
    def create(cls, deck: Deck | None = None) -> Player:
        return cls(deck=deck, role=Role.runner)

    # @property
    # def stack(self) -> Iterator[CardState]:
    #     return self.cards.in_zone(GameZone.deck)

    # @property
    # def grip(self) -> Iterator[CardState]:
    #     return self.cards.in_zone(GameZone.hand)

    # @property
    # def heap(self) -> Iterator[CardState]:
    #     return self.cards.in_zone(GameZone.discard)
