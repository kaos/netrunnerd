from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator

from netrunner.core.card_state import CardState
from netrunner.core.deck import Deck
from netrunner.core.error import GameError
from netrunner.core.zone import GameZone


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
    cards: tuple[CardState, ...] = ()

    @classmethod
    def create(cls) -> Player:
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

    def get_cards(self, zone: GameZone) -> Iterator[CardState]:
        for state in self.cards:
            if state.zone is zone:
                yield state


@dataclass(frozen=True)
class Corp(Player):
    """The Corp role."""

    @classmethod
    def create(cls) -> Player:
        return cls(role=Role.corp)

    @property
    def RnD(self) -> Iterator[CardState]:
        return self.get_cards(GameZone.deck)

    @property
    def HQ(self) -> Iterator[CardState]:
        return self.get_cards(GameZone.hand)

    @property
    def archives(self) -> Iterator[CardState]:
        return self.get_cards(GameZone.discard)


@dataclass(frozen=True)
class Runner(Player):
    """The Runner role."""

    @classmethod
    def create(cls) -> Player:
        return cls(role=Role.runner)

    @property
    def stack(self) -> Iterator[CardState]:
        return self.get_cards(GameZone.deck)

    @property
    def grip(self) -> Iterator[CardState]:
        return self.get_cards(GameZone.hand)

    @property
    def heap(self) -> Iterator[CardState]:
        return self.get_cards(GameZone.discard)
