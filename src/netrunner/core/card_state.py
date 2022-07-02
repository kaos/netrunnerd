from __future__ import annotations

from dataclasses import dataclass

from netrunner.core.card import Card
from netrunner.core.zone import GameZone


@dataclass(frozen=True)
class CardState:
    card: Card
    zone: GameZone
    active: bool = False
