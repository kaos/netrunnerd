from __future__ import annotations

import logging
from itertools import islice

from netrunner import api
from netrunner.daemon.client import ClientInfoImpl
from netrunner.daemon.game import GameID, GameState
from netrunner.daemon.player import PlayerImpl

logger = logging.getLogger(__name__)


class NetrunnerLobbyImpl(api.NetrunnerLobby.Server):
    client_info: ClientInfoImpl
    games: dict[GameID, GameState] = {}

    def __init__(self):
        logger.info("client connected")
        self.client_info = ClientInfoImpl("<no nick>")

    def myself(self, **kwargs) -> ClientInfoImpl:
        return self.client_info

    def listGames(self, page: int, pageSize: int, **kwargs) -> tuple[list[api.Game], int]:
        assert page > 0
        assert pageSize > 0
        start = (page - 1) * pageSize
        stop = start + pageSize - 1
        return [
            game.serialize(api.Role.spectator) for game in islice(self.games.values(), start, stop)
        ], len(self.games)

    def newGame(self, role: api.Role, **kwargs) -> PlayerImpl:
        player = PlayerImpl.create_game(role, self.client_info)
        self.games[player.state.id] = player.state
        print(f"New game: {player.state}")
        return player

    def joinGame(self, role: api.Role, gameId: api.Game.Id, **kwargs) -> PlayerImpl:
        state = self.games[GameID(**gameId.to_dict())]
        return PlayerImpl.join_game(role, state, self.client_info)
