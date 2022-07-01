from __future__ import annotations

from netrunner.core.game import Game


def test_create_game() -> None:
    assert Game.create()
