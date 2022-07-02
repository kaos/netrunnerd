from __future__ import annotations

from dataclasses import dataclass

from netrunner.core.game import Game


@dataclass(frozen=True)
class BeginGame:
    game: Game


@dataclass(frozen=True)
class GameState:
    game: Game
    turn: int
