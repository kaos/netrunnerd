from __future__ import annotations

import logging
from dataclasses import dataclass, field

import click

from netrunner import api
from netrunner.client.mode import mode

logger = logging.getLogger(__name__)


@dataclass
class NetrunnerLobby:
    root: api.NetrunnerLobby
    client_info: api.ClientInfo
    cmd: click.Command
    games: list[api.Player] = field(default_factory=list)

    def switch_mode(self, next_mode: str | None) -> None:
        if not next_mode:
            return
        if self.cmd.name == next_mode:
            click.echo(f"already in #{next_mode}")
            return

        self.cmd = mode.registry[next_mode]
        click.echo(f"switched to #{next_mode}")
