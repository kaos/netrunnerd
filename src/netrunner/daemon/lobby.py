from __future__ import annotations

from netrunner import api
from netrunner.daemon.game import GameImpl
from netrunner.daemon.player import PlayerImpl


class NetrunnerLobbyImpl(api.schema.NetrunnerLobby.Server):  # type: ignore[name-defined]
    client_info: ClientInfoImpl
    games: list[GameImpl] = []

    def __init__(self):
        self.client_info = ClientInfoImpl("<no nick>")

    def myself(self, **kwargs) -> ClientInfoImpl:
        return self.client_info

    def listGames(self, page: int, pageSize: int, **kwargs) -> tuple[list[GameImpl], int]:
        assert page > 0
        assert pageSize > 0
        start = (page - 1) * pageSize
        end = start + pageSize - 1
        return self.games[start:end], len(self.games)

    def newGame(self, role, **kwargs) -> PlayerImpl:
        game = GameImpl()
        self.games.append(game)
        return PlayerImpl(game, self.client_info.nick, role)


class ClientInfoImpl(api.schema.ClientInfo.Server):  # type: ignore[name-defined]
    nick: str

    def __init__(self, nick: str):
        self.nick = nick

    def getNick(self, **kwargs) -> str:
        return self.nick

    def setNick(self, nick: str, **kwargs) -> None:
        print(f"Change nick {self.nick} -> {nick}")
        self.nick = nick
