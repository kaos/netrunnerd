from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import ClassVar

from netrunner import api
from netrunner.annotations import CapAn
from netrunner.core.game import Game
from netrunner.core.player import Player

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GameID:
    seq: int
    pool: str


@dataclass(frozen=True)
class Attendee:
    nick: str
    role: api.Role


@dataclass
class GameState:
    _seq: ClassVar[int] = 0
    _pool: ClassVar[str] = str(datetime.now().date())

    id: GameID
    game: Game
    players: list[Attendee]

    @classmethod
    def create(cls, game: Game, nick: str, role: api.Role) -> GameState:
        cls._seq += 1
        id = GameID(cls._seq, cls._pool)

        return cls(id, game, [Attendee(nick, role)])

    def join(self, nick: str, role: api.Role) -> api.Role:
        for player in self.players:
            if player.nick == nick:
                raise ValueError(f"{nick} already joined this game")

        if role != api.Role.spectator:
            for player in self.players:
                if player.role == role:
                    logger.info(
                        f"{nick} can't join as {role} as that seat is taken, will be joining as spectator instead"
                    )
                    role = api.Role.spectator
                    break

        self.players.append(Attendee(nick, role))
        return role

    def serialize(self, role: api.Role) -> api.Game:
        return {
            "id": asdict(self.id),
            "corp": CorpParticipant(self).serialize(role),
            "runner": RunnerParticipant(self).serialize(role),
            "spectators": [
                player.nick for player in self.players if player.role == api.Role.spectator
            ],
        }

    def find_attendee(self, role: api.Role) -> Attendee | None:
        for player in self.players:
            if player.role == role:
                return player
        return None


@dataclass(frozen=True)
class Participant:
    role: ClassVar[api.Role]
    state: GameState

    @property
    def player(self) -> Player:
        raise NotImplementedError()

    def attendee(self) -> Attendee | None:
        return self.state.find_attendee(self.role)

    def serialize(self, role: api.Role) -> api.Game.Participant:
        attendee = self.attendee()
        if attendee is None:
            return {}

        participant = {
            "nickName": attendee.nick,
            "cards": [CapAn.serialize_dataclass(card) for card in self.player.cards],
        }
        deck = self.player.deck
        if deck:
            participant["deck"] = CapAn.serialize_dataclass(deck)
        return participant


class CorpParticipant(Participant):
    role = api.Role.corp

    @property
    def player(self) -> Player:
        return self.state.game.corp


class RunnerParticipant(Participant):
    role = api.Role.runner

    @property
    def player(self) -> Player:
        return self.state.game.runner
