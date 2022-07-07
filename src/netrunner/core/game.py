from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterator, cast

from netrunner.core.card_state import Cards
from netrunner.core.error import GameError
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

    def check(self) -> Iterator[GameError]:
        if len(self.players) != 2:
            yield GameError(f"Wrong number of participant players: {len(self.players)}.")
        for player in self.players:
            yield from player.check()

    def setup(self) -> Game:
        # § 1.6.4. Each player takes 5 credits from the bank.
        # § 1.6.5. Each player shuffles their deck.
        # § 1.6.6. Each player draws 5 cards.
        players = tuple(
            replace(
                player,
                credit_pool=5,
                cards=Cards.init(player.deck.shuffle()).draw(5),
            )
            for player in self.players
            if player.deck is not None
        )
        return replace(self, players=players)
