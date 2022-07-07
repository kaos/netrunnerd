from __future__ import annotations

from functools import reduce
from typing import Any, ClassVar, Mapping, cast

import click
from blinker import Signal


class AbortModeSwitch(Exception):
    pass


class mode:
    """A click.command factory."""

    registry: ClassVar[dict[str, click.Command]] = {}
    mode_names: ClassVar[list[str]] = []
    CONTEXT_SETTINGS: ClassVar[dict[str, Any]] = dict(help_option_names=["/help"])

    on_enter: ClassVar[Signal] = Signal()
    on_exit: ClassVar[Signal] = Signal()

    name: str
    kwargs: Mapping

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.kwargs = kwargs
        kwargs.setdefault("context_settings", self.CONTEXT_SETTINGS)

    def __call__(self, f) -> click.Command:
        cmd_mode = cast(
            click.Command,
            reduce(
                lambda f, decorator: decorator(f),  # type: ignore[operator]
                [
                    click.pass_obj,
                    click.command(self.name, **self.kwargs),
                ],
                f,
            ),
        )
        mode.registry[self.name] = cmd_mode
        mode.mode_names.append(self.name)
        return cmd_mode
