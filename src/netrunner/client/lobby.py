from __future__ import annotations

import logging
from dataclasses import dataclass, field

import click

from netrunner import api
from netrunner.client.message import MessageLinkImpl, Messages
from netrunner.client.mode import AbortModeSwitch, mode

logger = logging.getLogger(__name__)


@dataclass
class NetrunnerLobby:
    root: api.NetrunnerLobby
    client_info: api.ClientInfo
    cmd_mode: click.Command
    messages: Messages
    games: list[api.Player] = field(default_factory=list)

    def __post_init__(self):
        MessageLinkImpl.on_message.connect(self.receive_message)

    def receive_message(self, sender: str, message: str):
        click.echo(f"\r{sender}: {message}\n#{self.cmd_mode.name} $ ", nl=False)

    def switch_mode(self, next_mode: str | None) -> None:
        if not next_mode:
            return
        if self.cmd_mode.name == next_mode:
            click.echo(f"already in #{next_mode}")
            return

        try:
            mode.on_exit.send(self.cmd_mode, lobby=self)
            cmd = mode.registry[next_mode]
            mode.on_enter.send(cmd, lobby=self)
            self.cmd_mode = cmd
            click.echo(f"switched to #{next_mode}")
        except AbortModeSwitch as aborted:
            click.echo(f"did not switch to #{next_mode}: {aborted}")
