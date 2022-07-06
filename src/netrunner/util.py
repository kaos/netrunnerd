from __future__ import annotations

import asyncio
import shlex
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Any, Literal, Sequence, TypeVar, Union, cast, get_args, overload

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
