from __future__ import annotations

from typing import ClassVar, Iterator

from netrunner import api
from netrunner.core import player
from netrunner.core.game import Game
from netrunner.daemon.client import ClientInfoImpl
from netrunner.daemon.game import GameState


class PlayerImpl(api.Player.Server):
    role: ClassVar[api.Role]

    state: GameState
    nick: str

    @staticmethod
    def create_game(role: api.Role, client: ClientInfoImpl) -> PlayerImpl:
        if role == api.Role.corp:
            cls = CorpImpl
        elif role == api.Role.runner:
            cls = RunnerImpl
        elif role == api.Role.spectator:
            cls = SpectatorImpl
        else:
            raise ValueError(f"Invalid role: {role!r}")

        state = GameState.create(
            game=Game(players=tuple(cls.create_players())),
            nick=client.nick,
            role=role,
        )
        return cls(state, client.nick)

    @staticmethod
    def create_players() -> Iterator[player.Player]:
        return iter([])

    def __init__(self, state: GameState, nick: str):
        self.state = state
        self.nick = nick

    @property
    def player(self) -> player.Player:
        raise NotImplementedError("No player for this role.")

    def getInfo(self, **kwargs):
        return self.nick, self.role

    def getGame(self, **kwargs):
        return self.state.serialize(self.role)


class CorpImpl(PlayerImpl, api.Corp.Server):
    role = api.Role.corp

    @staticmethod
    def create_players() -> Iterator[player.Player]:
        yield player.Corp.create()

    @property
    def player(self) -> player.Corp:
        return self.state.game.corp


class RunnerImpl(PlayerImpl, api.Runner.Server):
    role = api.Role.runner

    @staticmethod
    def create_players() -> Iterator[player.Player]:
        yield player.Runner.create()

    @property
    def player(self) -> player.Runner:
        return self.state.game.runner


class SpectatorImpl(PlayerImpl, api.Spectator.Server):
    role = api.Role.spectator
