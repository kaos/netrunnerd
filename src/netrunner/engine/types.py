from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, ClassVar, Mapping

from netrunner.core.game import Game


@dataclass(frozen=True)
class BeginGame:
    game: Game


@dataclass(frozen=True)
class GameState:
    game: Game
    turn: int


@dataclass(frozen=True)
class DecklistRequest:
    _netrunner_db_api_root: ClassVar[str] = "https://netrunnerdb.com/api/2.0/public/decklist/"

    url: str

    def __post_init__(self):
        if self.url.startswith(self._netrunner_db_api_root):
            return

        decklist_id = ""
        if self.url.startswith("https://netrunnerdb.com/"):
            m = re.search("/decklist/([^/]+)", self.url)
            decklist_id = m and m.group(1)
        elif not self.url.startswith("http"):
            decklist_id = self.url

        if not decklist_id:
            return

        # Update self.url, side-stepping the frozen self.
        object.__setattr__(self, "url", self._netrunner_db_api_root + decklist_id)


@dataclass(frozen=True)
class Decklist:
    total: int
    success: bool
    version_number: str
    last_updated: str
    data: tuple[Mapping[str, Any]]
