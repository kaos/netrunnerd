from __future__ import annotations

from typing import cast

import pytest

from netrunner.core.game import Game
from netrunner.core.player import Role


def test_create_game() -> None:
    assert Game.create()


def test_game_has_two_players_with_proper_roles() -> None:
    """Rule § 1.1.1."""
    game = Game.create()
    assert len(game.players) == 2
    assert game.runner is not None
    assert game.corp is not None

    with pytest.raises(RuntimeError):
        game.get_player(cast(Role, 0))
