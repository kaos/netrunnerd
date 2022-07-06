from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from netrunner.core.game import Game


@dataclass(frozen=True)
class BeginGame:
    game: Game


@dataclass(frozen=True)
class GameState:
    game: Game
    turn: int


@dataclass(frozen=True)
class DecklistRequest:
    url: str


@dataclass(frozen=True)
class Decklist:
    total: int
    success: bool
    version_number: str
    last_updated: str
    data: tuple[Mapping[str, Any]]
