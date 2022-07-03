from __future__ import annotations

from netrunner import api


class NetrunnerLobbyImpl(api.schema.NetrunnerLobby.Server):  # type: ignore[name-defined]
    client_info: ClientInfoImpl

    def __init__(self):
        self.client_info = ClientInfoImpl("<no nick>")

    def myself(self, **kwargs) -> ClientInfoImpl:
        return self.client_info


class ClientInfoImpl(api.schema.ClientInfo.Server):  # type: ignore[name-defined]
    def __init__(self, nick: str):
        self.nick = nick

    def getNick(self, **kwargs) -> str:
        return self.nick

    def setNick(self, nick: str, **kwargs) -> None:
        print(f"Change nick {self.nick} -> {nick}")
        self.nick = nick
