from __future__ import annotations

from dataclasses import asdict, dataclass

from netrunner import api
from netrunner.core.game import Game


@dataclass(frozen=True)
class GameID:
    seq: int
    pool: str


@dataclass
class GameState:
    id: GameID
    game: Game
    corp_nick: str | None = None
    runner_nick: str | None = None

    @classmethod
    def create(cls, game: Game, nick: str, role: api.Role) -> GameState:
        id = GameID(123, "2022-07-04")
        role_nick = {}
        if role == api.Role.corp:
            role_nick["corp_nick"] = nick
        elif role == api.Role.runner:
            role_nick["runner_nick"] = nick
        return cls(id, game, **role_nick)

    def serialize(self, role: api.Role) -> api.Game:
        return {
            "id": asdict(self.id),
        }
