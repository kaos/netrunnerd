from __future__ import annotations

from pants.engine.rules import collect_rules, rule

from netrunner.core.error import GameError
from netrunner.engine.types import BeginGame, GameState


@rule
async def begin(begin: BeginGame) -> GameState:
    """Prepare for a new game."""
    game = begin.game
    GameError.assert_no_issues(game.check())
    game.setup()
    return GameState(game, turn=0)


def rules():
    return collect_rules()
