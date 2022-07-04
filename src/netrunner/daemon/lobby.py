from __future__ import annotations

from netrunner import api
from netrunner.daemon.client import ClientInfoImpl
from netrunner.daemon.game import GameState
from netrunner.daemon.player import PlayerImpl


class NetrunnerLobbyImpl(api.NetrunnerLobby.Server):
    client_info: ClientInfoImpl
    games: list[GameState] = []

    def __init__(self):
        self.client_info = ClientInfoImpl("<no nick>")

    def myself(self, **kwargs) -> ClientInfoImpl:
        return self.client_info

    def listGames(self, page: int, pageSize: int, **kwargs) -> tuple[list[api.Game], int]:
        assert page > 0
        assert pageSize > 0
        start = (page - 1) * pageSize
        end = start + pageSize - 1
        return [game.serialize(api.Role.spectator) for game in self.games[start:end]], len(
            self.games
        )

    def newGame(self, role: api.Role, **kwargs) -> PlayerImpl:
        player = PlayerImpl.create_game(role, self.client_info)
        self.games.append(player.state)
        print(f"New game: {player.state}")
        return player

    def joinGame(self, role, gameId, **kwargs) -> PlayerImpl:
        ...
