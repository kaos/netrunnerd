from __future__ import annotations

from enum import Enum
from typing import Any, TypeVar, Union, get_args

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
                return enum

        raise ValueError(f"Unkonwn enum value {value!r} in {union_type}.")
