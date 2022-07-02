from __future__ import annotations

from typing import Iterator


class GameError(Exception):
    """Netrunner game error.\n."""

    @classmethod
    def assert_no_issues(cls, issues: Iterator[GameError]) -> None:
        message = "\n".join(map(str, issues))
        if message:
            raise cls(message)

    def __str__(self) -> str:
        s = super().__str__()
        prefix = type(self).__doc__
        if prefix:
            # docformatter insists on adding a final period on the doc string.
            prefix = prefix.replace("\n.", "\n")
            if not prefix.endswith("\n"):
                prefix += ": "
            return prefix + s
        return s
