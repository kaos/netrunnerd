from __future__ import annotations

from netrunner import api


class NetrunnerLobbyImpl(api.schema.NetrunnerLobby.Server):
    def __init__(self):
        self.client_info = ClientInfoImpl("<no nick>")

    def myself(self, **kwargs) -> ClientInfoImpl:
        return self.client_info


class ClientInfoImpl(api.schema.ClientInfo.Server):
    def __init__(self, nick: str):
        self.nick = nick

    def getNick(self, **kwargs) -> str:
        return self.nick

    def setNick(self, params, **kwargs) -> None:
        assert len(params) == 1
        self.nick = params[0]
