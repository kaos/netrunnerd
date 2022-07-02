from __future__ import annotations

from netrunner.util import EnumUnion


class CorpEnum(EnumUnion):
    @staticmethod
    def _select(**kwargs) -> bool:
        return kwargs == dict(side="corp")


class RunnerEnum(EnumUnion):
    @staticmethod
    def _select(**kwargs) -> bool:
        return kwargs == dict(side="runner")
