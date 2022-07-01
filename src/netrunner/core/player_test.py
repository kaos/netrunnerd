from __future__ import annotations

from netrunner.core.player import Player, Role


def test_common_player_attributes() -> None:
    """Game concepts."""
    player = Player(Role.runner)

    # § 1.1.2: Legal deck check.
    assert not player.has_legal_deck
