from __future__ import annotations

from dataclasses import replace
from typing import ClassVar, Iterator

from netrunner import api
from netrunner.core import player
from netrunner.core.deck import Deck
from netrunner.core.game import Game
from netrunner.daemon.client import ClientInfoImpl
from netrunner.daemon.game import GameState


class PlayerImpl(api.Player.Server):
    role: ClassVar[api.Role]

    state: GameState
    nick: str

    @classmethod
    def get_impl(cls, role: api.Role) -> type[PlayerImpl]:
        for impl in cls.__subclasses__():
            if impl.role == role:
                return impl
        raise NotImplementedError(f"No player implementation for role: {role!r}")

    @classmethod
    def join_game(cls, role: api.Role, state: GameState, client: ClientInfoImpl) -> PlayerImpl:
        role = state.join(client.nick, role)
        impl = cls.get_impl(role)
        state.game = replace(
            state.game, players=(*state.game.players, *impl.create_players(client.deck))
        )
        return impl(state, client.nick)

    @classmethod
    def create_game(cls, role: api.Role, client: ClientInfoImpl) -> PlayerImpl:
        impl = cls.get_impl(role)
        state = GameState.create(
            game=Game(players=tuple(impl.create_players(client.deck))),
            nick=client.nick,
            role=role,
        )
        return impl(state, client.nick)

    @classmethod
    def create_players(cls, deck: Deck | None) -> Iterator[player.Player]:
        player_cls = cls.get_player_class()
        if player_cls is not None:
            yield player_cls.create(deck=deck)

    @staticmethod
    def get_player_class() -> type[player.Player] | None:
        return None

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
    def get_player_class() -> type[player.Player] | None:
        return player.Corp

    @property
    def player(self) -> player.Corp:
        return self.state.game.corp


class RunnerImpl(PlayerImpl, api.Runner.Server):
    role = api.Role.runner

    @staticmethod
    def get_player_class() -> type[player.Player] | None:
        return player.Runner

    @property
    def player(self) -> player.Runner:
        return self.state.game.runner


class SpectatorImpl(PlayerImpl, api.Spectator.Server):
    role = api.Role.spectator
