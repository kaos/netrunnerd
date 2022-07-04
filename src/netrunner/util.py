from __future__ import annotations

import asyncio
import shlex
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Any, Dict, Literal, Mapping, Sequence, TypeVar, Union, cast, get_args, overload

import click

T = TypeVar("T")


class EnumUnion(Enum):
    @staticmethod
    def _select(**select) -> bool:
        return not select

    @staticmethod
    def find_value(union: Union[T], value: Any, **select) -> T:
        for union_type in get_args(union):
            if issubclass(union_type, EnumUnion) and union_type._select(**select):
                break
        else:
            raise TypeError(f"Unknown enum type {select} for {union}.")

        for enum in union_type:
            if enum.value == value:
                return cast(T, enum)

        raise ValueError(f"Unkonwn enum value {value!r} in {union_type}.")


@overload
async def ainput(prompt: str, split: Literal[True]) -> Sequence[str]:
    ...


@overload
async def ainput(prompt: str, split: Literal[False]) -> str:
    ...


async def ainput(prompt: str = "", split: bool = True):
    with ThreadPoolExecutor(1, "AsyncInput") as executor:
        s = await asyncio.get_event_loop().run_in_executor(executor, input, prompt)
        return s if not split else shlex.split(s)


class cli_command:
    registry: Dict[str, click.Command] = {}
    command_names: list[str] = []
    CONTEXT_SETTINGS = dict(help_option_names=["/help"])

    name: str
    kwargs: Mapping

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.kwargs = kwargs
        kwargs.setdefault("context_settings", self.CONTEXT_SETTINGS)

    def __call__(self, f) -> click.Command:
        cmd = cast(click.Command, click.command(self.name, **self.kwargs)(f))
        cli_command.registry[self.name] = cmd
        cli_command.command_names.append(self.name)
        return cmd
