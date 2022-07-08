from __future__ import annotations

from typing import Callable

from netrunner import api


class MessageLinkImpl(api.ClientInfo.MessageLink.Server):
    def __init__(self, deliver_message: Callable):
        self.deliver_message = deliver_message

    def message(self, nick: str, message: str, **kwargs):
        self.deliver_message(nick, message)
