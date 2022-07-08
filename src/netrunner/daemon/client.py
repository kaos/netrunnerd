from __future__ import annotations

from blinker import Signal

from netrunner import api
from netrunner.annotations import CapAn
from netrunner.core.deck import Deck
from netrunner.daemon.message import MessageLinkImpl


class InvalidNickName(Exception):
    pass


class ClientInfoImpl(api.ClientInfo.Server):
    on_change_nick = Signal()

    nick: str
    deck: Deck | None
    msg_receiver: api.ClientInfo.MessageLink | None
    msg_sender: MessageLinkImpl

    def __init__(self, nick: str, msg_sender: MessageLinkImpl):
        self.nick = nick
        self.deck = None
        self.msg_receiver = None
        self.msg_sender = msg_sender

    def close(self):
        self.nick = ""
        self.msg_receiver = None
        self.deck = None

    def getNick(self, **kwargs) -> str:
        return self.nick or "<no nick>"

    def setNick(self, nick: str, password: str, **kwargs) -> None:
        if len(nick) < 2:
            raise InvalidNickName("Nick name must be at least 2 characters long.")

        self.on_change_nick.send(self, nick=nick, password=password)
        if self.nick:
            print(f"change nick {self.nick} -> {nick}")
        else:
            print(f"set nick {nick}")
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

    def messages(self, receiver: api.ClientInfo.MessageLink, **kwargs):
        self.msg_receiver = receiver
        return self.msg_sender

    def send_message(self, nick: str, message: str):
        if self.msg_receiver:
            self.msg_receiver.message(nick=nick, message=message)
