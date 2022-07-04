from __future__ import annotations

from pants.engine.rules import collect_rules, rule, QueryRule, Get

from netrunner.core.error import GameError
from netrunner.engine.types import BeginGame, GameState
from netrunner.engine.types import Decklist, DecklistRequest
import requests


@rule
async def begin(begin: BeginGame) -> GameState:
    """Prepare for a new game."""
    game = begin.game
    GameError.assert_no_issues(game.check())
    game.setup()
    return GameState(game, turn=0)


@rule
async def download_decklist(request: DecklistRequest) -> Decklist:
    return Decklist(**requests.get(request.url).json())


def rules():
    return (
        *collect_rules(),
        QueryRule(GameState, (BeginGame,)),
        QueryRule(Decklist, (DecklistRequest,)),
    )
