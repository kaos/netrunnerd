from __future__ import annotations

import math
from datetime import datetime
from typing import ClassVar

import click

from netrunner.client.cmd import command


class list_games(command):
    click_args = ("/list",)
    click_kwargs = dict(
        metavar="PAGE", type=int, is_flag=False, flag_value=1, help="List games page"
    )
    click_options = (click.option("/page-size", type=int, help="List games page size"),)
    default_page_size: ClassVar[int] = 25

    async def do_invoke(self, list_games: int, page_size: int, **kwargs):
        if page_size and page_size != self.default_page_size:
            type(self).default_page_size = page_size
            click.echo(f"page size changed to {page_size}")
        else:
            page_size = self.default_page_size

        res = await self.lobby.root.listGames(page=list_games, pageSize=page_size).a_wait()
        if not res.totalCount:
            click.echo("there are no games\n")
        else:
            pages = math.ceil(res.totalCount / page_size)
            for game in res.games:
                click.echo(f"-- game:\n{game}")
            click.echo(f"\n// page {list_games}/{pages} || {res.totalCount} games in total\n")


def parse_game_id(ctx, param, value):
    if not value:
        return None
    try:
        seq, use_pool, pool = value.partition(":")
        return dict(seq=int(seq), pool=pool if use_pool else str(datetime.now().date()))
    except ValueError:
        raise click.BadParameter(f"Expected game id `SEQ[:POOL]`, but got {value!r}.")


class join_game(command):
    click_args = ("/join",)
    click_kwargs = dict(
        type=click.Choice(("corp", "runner", "spectate")),
        help="Join game identified by the /game option",
    )
    click_options = (
        click.option(
            "/game",
            "game_id",
            metavar="GAME_ID",
            callback=parse_game_id,
            help="Game id is `SEQ[:POOL]` where the optional POOL defaults to todays pool.",
        ),
    )

    async def do_invoke(self, join_game: str, game_id: dict | None, **kwargs):
        if not game_id:
            click.echo(
                "must specify which game to join (with /game GAME_ID), "
                "run /list to see available games."
            )
            return

        player = (await self.lobby.root.joinGame(role=join_game, gameId=game_id).a_wait()).player
        click.echo(f"joined game {await player.getInfo().a_wait()}")
        if not self.next_mode:
            self.next_mode = "game"


class new_game(command):
    click_args = ("/new",)
    click_kwargs = dict(type=click.Choice(("corp", "runner")), help="Create new game")

    async def do_invoke(self, new_game: str, **kwargs):
        player = (await self.lobby.root.newGame(role=new_game).a_wait()).player
        click.echo(f"created game for {await player.getInfo().a_wait()}")
        if not self.next_mode:
            self.next_mode = "game"