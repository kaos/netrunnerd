from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from netrunner.core.player import Corp, Player, Role, Runner


@dataclass(frozen=True)
class Game:
    """The core data for a single game."""

    players: tuple[Player, ...]

    @classmethod
    def create(cls) -> Game:
        """Create a new Game object."""
        return cls(
            players=(
                Corp.create(),
                Runner.create(),
            ),
        )

    @property
    def corp(self) -> Corp:
        return cast(Corp, self.get_player(Role.corp))

    @property
    def runner(self) -> Runner:
        return cast(Runner, self.get_player(Role.runner))

    def get_player(self, role: Role) -> Player:
        for player in self.players:
            if player.role == role:
                return player
        raise RuntimeError(f"No player with role: {role}.")
