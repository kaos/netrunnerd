from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Game:
    """The core data for a single game."""

    @classmethod
    def create(cls) -> Game:
        """Create a new Game object."""
        return cls()
