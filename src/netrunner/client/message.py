from __future__ import annotations

from dataclasses import dataclass

from blinker import Signal

from netrunner import api


class MessageLinkImpl(api.ClientInfo.MessageLink.Server):
    on_message = Signal()

    def message(self, nick: str, message: str, **kwargs):
        self.on_message.send(nick, message=message)


@dataclass
class Messages:
    receiver: MessageLinkImpl
    sender: api.ClientInfo.MessageLink

    async def send(self, nick: str, message: str):
        await self.sender.message(nick=nick, message=message).a_wait()
