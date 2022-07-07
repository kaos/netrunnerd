from __future__ import annotations

from netrunner import api
from netrunner.annotations import CapAn
from netrunner.core.deck import Deck


class ClientInfoImpl(api.ClientInfo.Server):
    nick: str
    deck: Deck | None

    def __init__(self, nick: str):
        self.nick = nick
        self.deck = None

    def getNick(self, **kwargs) -> str:
        return self.nick

    def setNick(self, nick: str, password: str, **kwargs) -> None:
        print(f"Change nick {self.nick} -> {nick}")
        self.nick = nick

    def registerNick(self, nick: str, password: str, **kwargs) -> None:
        pass

    def getDeck(self, **kwargs) -> api.Deck:
        if not self.deck:
            return None
        else:
            return CapAn.serialize_dataclass(self.deck)

    def setDeck(self, deck: api.Deck, **kwargs) -> None:
        print(f"Set deck: {deck.name!r} for {self.nick}")
        self.deck = CapAn.deserialize_dataclass(Deck, deck)
