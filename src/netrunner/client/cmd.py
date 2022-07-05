from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, ClassVar

import click

from netrunner.client.lobby import NetrunnerLobby
from netrunner.client.mode import mode


@dataclass
class command:
    command: ClassVar[Callable[..., Any] | click.Command]

    lobby: NetrunnerLobby
    next_mode: str | None = None

    async def invoke(self, **kwargs):
        for cls in type(self).__subclasses__():
            if kwargs.get(cls.__name__) is not None:
                cmd = cls(self.lobby, self.next_mode)
                await cmd.do_invoke(**kwargs)
                if cmd.next_mode:
                    self.next_mode = cmd.next_mode
        self.lobby.switch_mode(self.next_mode)


class mode(command):
    command: ClassVar[Callable[..., Any] | click.Command] = click.argument(
        "mode",
        nargs=1,
        required=False,
        type=click.Choice(mode.mode_names),
    )

    async def do_invoke(self, mode: str | None, **kwargs):
        if mode:
            self.next_mode = mode
