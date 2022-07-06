from __future__ import annotations

import click

from netrunner.client.cmd import command


class list_decks(command):
    click_args = ("/decks",)
    click_kwargs = dict(metavar="DECKLIST", help="List decks in DECKLIST")

    async def do_invoke(self, list_decks: str, **kwargs):
        decks = (await self.lobby.root.listDecks(decklist=list_decks).a_wait()).decks

        print(f"\nDECKS:\n{decks}\n\n")

        for deck in decks:
            click.echo(f"== {deck.name}")
            for entry in deck.cards:
                click.echo(f" - {entry.count}x {entry.card.name}")
