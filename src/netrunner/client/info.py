from __future__ import annotations

from typing import Any, Callable, ClassVar

import click

from netrunner.client.cmd import command


class nick(command):
    command: ClassVar[Callable[..., Any] | click.Command] = click.option(
        "/nick",
        metavar="NAME",
        help="Change nick name",
    )

    async def do_invoke(self, nick: str, **kwargs):
        await self.lobby.client_info.setNick(nick=nick).a_wait()
        click.echo(f"nick name changed to {nick!r}")


# nick, whoami, list_decks, list_games, join_game, game_id, new_game
