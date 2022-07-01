from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from netrunner.core.deck import Deck


class Role(Enum):
    corp = 1
    runner = 2


@dataclass(frozen=True)
class Player:
    """The core data for a player."""

    role: Role
    deck: Deck | None = None

    @classmethod
    def create(cls) -> Player:
        raise NotImplementedError()

    @property
    def has_legal_deck(self) -> bool:
        if not self.deck:
            return False
        return self.deck.is_legal


@dataclass(frozen=True)
class Corp(Player):
    """The Corp role."""

    @classmethod
    def create(cls) -> Player:
        return cls(role=Role.corp)


@dataclass(frozen=True)
class Runner(Player):
    """The Runner role."""

    @classmethod
    def create(cls) -> Player:
        return cls(role=Role.runner)
