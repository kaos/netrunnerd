from __future__ import annotations

import requests
from pants.engine.rules import QueryRule, collect_rules, rule

from netrunner.core.error import GameError
from netrunner.engine.types import BeginGame, Decklist, DecklistRequest, GameState


@rule
async def begin(begin: BeginGame) -> GameState:
    """Prepare for a new game.

    § 1.6.
    """
    game = begin.game
    GameError.assert_no_issues(game.check())
    return GameState(game.setup(), turn=0)


@rule
async def download_decklist(request: DecklistRequest) -> Decklist:
    return Decklist(**requests.get(request.url).json())


def rules():
    return (
        *collect_rules(),
        QueryRule(GameState, (BeginGame,)),
        QueryRule(Decklist, (DecklistRequest,)),
    )
