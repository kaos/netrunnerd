from __future__ import annotations

from enum import Enum


class GameZone(Enum):
    """§ 4.1.1.a lists 8 game zones for cards and counters."""

    deck = 0
    hand = 1
    discard = 2
    score_area = 3
    play_area = 4
    bank = 5
    set_aside = 6
    removed_from_game = 7
