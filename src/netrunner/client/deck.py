from __future__ import annotations

from itertools import groupby

import click

from netrunner.client.cmd import command


def card_type(entry):
    return entry.card.which()


def keywords(card):
    sub = getattr(card, card.which())
    s = getattr(sub, "keywords", "")
    return f" [{s}]" if s else ""


def groupby_sort(data, key):
    return groupby(sorted(data, key=key), key=key)


class list_decks(command):
    click_args = ("/decks",)
    click_kwargs = dict(metavar="DECKLIST", help="List decks in DECKLIST")

    async def do_invoke(self, list_decks: str, **kwargs):
        decks = (await self.lobby.root.listDecks(decklist=list_decks).a_wait()).decks

        for deck in decks:
            click.echo(f"== {deck.name}")
            total_influence = 0
            for group, entries in groupby_sort(deck.cards, key=card_type):
                click.echo(f" ## {group.capitalize()}")
                for entry in entries:
                    c = entry.card
                    if c.faction.name != deck.identity.faction.name:
                        total_influence += c.influence * entry.count
                        used_influence = " " + ("•" * c.influence * entry.count)
                    else:
                        used_influence = ""

                    name = f"{c.name}{used_influence}"
                    click.echo(f" - {entry.count}x {name:<30}{keywords(c)}")
                click.echo()

            ident = deck.identity.identity
            click.echo(
                f" : {sum(entry.count for entry in deck.cards)} cards (min {ident.minimumDeckSize})\n"
                f" : {total_influence} influence spent (max {ident.influenceLimit})"
                "\n"
            )
