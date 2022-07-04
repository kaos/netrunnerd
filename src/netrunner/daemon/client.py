from __future__ import annotations

from netrunner import api


class ClientInfoImpl(api.ClientInfo.Server):
    nick: str

    def __init__(self, nick: str):
        self.nick = nick

    def getNick(self, **kwargs) -> str:
        return self.nick

    def setNick(self, nick: str, **kwargs) -> None:
        print(f"Change nick {self.nick} -> {nick}")
        self.nick = nick
