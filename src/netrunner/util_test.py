from __future__ import annotations

from typing import Union, cast

import pytest

from netrunner.util import EnumUnion


class AEnum(EnumUnion):
    @staticmethod
    def _select(**kwargs) -> bool:
        return kwargs == dict(code="A")


class BEnum(EnumUnion):
    @staticmethod
    def _select(**kwargs) -> bool:
        return kwargs == dict(code="B")


class A(AEnum):
    opt1 = "opt1"
    opt2 = "opt2"


class B(BEnum):
    opt2 = "opt2"
    opt3 = "opt3"


AB = Union[A, B]


@pytest.mark.parametrize(
    "code, value, expect",
    [
        ("A", "opt1", A.opt1),
        ("A", "opt2", A.opt2),
        ("B", "opt2", B.opt2),
        ("B", "opt3", B.opt3),
    ],
)
def test_enum_union_find_value(code: str, value: str, expect: A | B) -> None:
    actual: AB = cast(AB, EnumUnion.find_value(AB, value, code=code))
    assert expect is actual
