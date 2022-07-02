from __future__ import annotations

import pytest
from pants.engine.internals.scheduler import ExecutionError
from pants.engine.rules import QueryRule
from underpants.engine import RulesEngine, TestRulesEngine

from netrunner.core.game import Game
from netrunner.engine.rules import rules
from netrunner.engine.types import BeginGame, GameState


@pytest.fixture
def engine() -> RulesEngine:
    return TestRulesEngine.create_with_rules(
        *rules(),
        QueryRule(GameState, (BeginGame,)),
    )


@pytest.fixture
def game() -> Game:
    return Game.create()


def test_begin_game_issues(engine: RulesEngine) -> None:
    err = r"GameError: Netrunner game error\.\nCorp: missing deck\nRunner: missing deck"
    with pytest.raises(ExecutionError, match=err):
        engine.request(GameState, BeginGame(Game.create()))
