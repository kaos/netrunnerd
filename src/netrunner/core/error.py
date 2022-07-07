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


class DeckError(GameError):
    """Deck error base class."""


class OutOfCardsError(DeckError):
    """Player has no more cards to draw."""


class DeckCardLimitError(DeckError):
    """Deck has not enough cards."""

    def __init__(self, num_cards: int, min_cards: int) -> None:
        self.num_cards = num_cards
        self.min_cards = min_cards
        super().__init__(f"{num_cards} is less than {min_cards}.")


class DeckInfluenceOverspentError(DeckError):
    """Deck uses more influence from other factions than the current identity
    allows."""

    def __init__(self, influence_limit: int, influence_used: int) -> None:
        self.influence_limit = influence_limit
        self.influence_used = influence_used
        super().__init__(f"{influence_used} is more than {influence_limit}.")
