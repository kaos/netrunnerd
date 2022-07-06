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


def print_deck(deck):
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


class list_decks(command):
    click_args = ("/decks",)
    click_kwargs = dict(metavar="DECKLIST", help="List decks in DECKLIST")

    @staticmethod
    async def get_decks(cmd: command, decklist: str):
        return (await cmd.lobby.root.listDecks(decklist=decklist).a_wait()).decks

    async def do_invoke(self, list_decks: str, **kwargs):
        decks = await self.get_decks(self, list_decks)

        for deck in decks:
            print_deck(deck)


class select_deck(command):
    click_kwargs = dict(
        metavar="DECKLIST[:IDX]", help="Select deck from DECKLIST, IDX defaults to 0."
    )

    async def do_invoke(self, select_deck: str, **kwargs):
        decklist, _, idx = select_deck.partition(":")
        deck = (await list_decks.get_decks(self, decklist))[idx or 0]
        await self.lobby.client_info.setDeck(deck).a_wait()
        click.echo(f"selected deck: {deck.name}")


class show_deck(command):
    click_kwargs = dict(is_flag=True, default=None, help="Show your selected deck.")

    async def do_invoke(self, **kwargs):
        rsp = await self.lobby.client_info.getDeck().a_wait()
        if not rsp:
            click.echo("no deck selected. see help for /select-deck\n")
        else:
            print_deck(rsp.deck)
