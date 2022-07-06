from __future__ import annotations

from netrunner.util import EnumUnion


class SideEnum(EnumUnion):
    @classmethod
    def _select(cls, **kwargs) -> bool:
        return kwargs == dict(side=cls._get_side())

    @classmethod
    def _get_side(cls) -> str:
        raise NotImplementedError()


class CorpEnum(SideEnum):
    @classmethod
    def _get_side(cls) -> str:
        return "corp"


class RunnerEnum(SideEnum):
    @classmethod
    def _get_side(cls) -> str:
        return "runner"
