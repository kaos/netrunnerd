from __future__ import annotations

import logging
from itertools import islice
from queue import Queue
from typing import ClassVar

from underpants.engine import RulesEngine

from netrunner import api
from netrunner.annotations import CapAn
from netrunner.daemon.client import ClientInfoImpl
from netrunner.daemon.deck import DeckInfo
from netrunner.daemon.game import GameID, GameState
from netrunner.daemon.message import MessageLinkImpl
from netrunner.daemon.player import PlayerImpl
from netrunner.db.cardpool import create_card

logger = logging.getLogger(__name__)


class NickTakenError(Exception):
    pass


class NickNotSetError(Exception):
    pass


class NetrunnerLobbyImpl(api.NetrunnerLobby.Server):
    _inst: ClassVar[Queue] = Queue()
    engine: ClassVar[RulesEngine]
    games: ClassVar[dict[GameID, GameState]] = {}
    lobbies: ClassVar[list[NetrunnerLobbyImpl]] = []

    client_info: ClientInfoImpl

    def __new__(cls):
        if not cls._inst.empty():
            return cls._inst.get_nowait()
        else:
            return super().__new__(cls)

    def __init__(self):
        self.client_info = ClientInfoImpl("", MessageLinkImpl(self.deliver_message))
        self.init()

    def init(self):
        logger.info("client connected")
        self.lobbies.append(self)

    def __del__(self):
        self.close()

    def __str__(self):
        return self.client_info.getNick()

    def __repr__(self):
        return f"<Lobby: {self}>"

    def close(self):
        if self in self.lobbies:
            logger.debug(f"remove lobby {self}")
            self.lobbies.remove(self)

        self.client_info.close()
        self._inst.put_nowait(self)

    @ClientInfoImpl.on_change_nick.connect
    def on_change_nick(sender: ClientInfoImpl, nick: str, password: str):
        for lobby in NetrunnerLobbyImpl.lobbies:
            if sender is lobby.client_info:
                continue
            if lobby.client_info.nick == nick:
                raise NickTakenError(
                    f"Can not change nick name to {nick!r}, as it is already in use."
                )

    def check_nick(self):
        if not self.client_info.nick:
            raise NickNotSetError("Nick name required.")

    def broadcast(self, message: str):
        self.check_nick()
        nick = self.client_info.getNick()
        for lobby in self.lobbies:
            lobby.client_info.send_message(nick, message)

    def deliver_message(self, nick: str, message: str):
        self.check_nick()
        for lobby in self.lobbies:
            if lobby.client_info.nick == nick:
                print(f"msg {self.client_info.nick} -> {nick}: {message}")
                return lobby.client_info.send_message(self.client_info.nick, message)

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
        self.check_nick()
        player = PlayerImpl.create_game(role, self.client_info)
        self.games[player.state.id] = player.state
        print(f"{self.client_info.nick}: created game {player.state.id}")
        return player

    def joinGame(self, role: api.Role, gameId: api.Game.Id, **kwargs) -> PlayerImpl:
        self.check_nick()
        state = self.games[GameID(**gameId.to_dict())]
        print(f"{self.client_info.nick}: joining game {state.id}...")
        return PlayerImpl.join_game(role, state, self.client_info)

    def listDecks(self, decklist: str, **kwargs) -> list[api.Deck]:
        res = DeckInfo.list_decks(self.engine, decklist)
        return list(map(CapAn.serialize_dataclass, DeckInfo.iter_decks(res)))

    def viewCard(self, cardCode: str, **kwargs) -> api.Card:
        card = CapAn.serialize_dataclass(create_card(code=cardCode))
        return card

    def online(self, **kwargs) -> list[str]:
        return list(map(str, self.lobbies))
