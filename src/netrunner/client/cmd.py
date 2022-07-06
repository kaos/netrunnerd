from __future__ import annotations

from dataclasses import dataclass
from functools import partial, reduce
from typing import Any, Callable, ClassVar

import click
from click.decorators import FC

from netrunner.client.lobby import NetrunnerLobby
from netrunner.client.mode import mode


@dataclass
class command:
    click_decorator: ClassVar[Callable[..., Callable[..., Any] | click.Command]] = click.option
    click_args: ClassVar[tuple[str, ...]] = ()
    click_kwargs: ClassVar[dict[str, Any]] = {}
    click_options: ClassVar[tuple[Callable[[FC], FC], ...]] = ()

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

    @classmethod
    def command(cls, *args, **kwargs) -> Callable[..., Any] | click.Command:
        names = (cls.__name__, f"/{cls.__name__.replace('_', '-')}")
        args = cls.click_args + args
        if not any(arg in names for arg in args):
            if args or cls.click_decorator is click.argument:
                idx = 0
            else:
                idx = 1
            args += names[idx : idx + 1]
        return partial(
            reduce,
            lambda f, decorator: decorator(f),
            [
                cls.click_decorator(*args, **{**cls.click_kwargs, **kwargs}),
                *cls.click_options,
            ],
        )


class select_mode(command):
    click_decorator = click.argument
    click_kwargs = dict(
        nargs=1,
        required=False,
        type=click.Choice(mode.mode_names),
    )

    async def do_invoke(self, select_mode: str, **kwargs):
        self.next_mode = select_mode
