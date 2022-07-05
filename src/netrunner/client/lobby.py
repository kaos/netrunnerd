from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import datetime

import click
from netrunner.util import cli_command

from netrunner import api

logger = logging.getLogger(__name__)
PAGE_SIZE = 25
command_argument = click.argument(
    "command",
    nargs=1,
    required=False,
    type=click.Choice(cli_command.command_names),
)


def parse_game_id(ctx, param, value):
    if not value:
        return None
    try:
        seq, use_pool, pool = value.partition(":")
        return dict(seq=int(seq), pool=pool if use_pool else str(datetime.now().date()))
    except ValueError:
        raise click.BadParameter(f"Expected game id `SEQ[:POOL]`, but got {value!r}.")


@dataclass
class NetrunnerLobby:
    root: api.NetrunnerLobby
    client_info: api.ClientInfo
    cmd: click.Command

    def switch_cmd(self, command: str) -> None:
        if not command:
            return
        if self.cmd.name == command:
            click.echo(f"already in #{command}")
            return

        self.cmd = cli_command.registry[command]
        click.echo(f"switched to #{self.cmd.name}")


@cli_command("lobby")
@click.option("/nick", metavar="NAME", help="Change nick name")
@click.option("/whoami", is_flag=True, help="Check nick name")
@click.option("/decks", "list_decks", metavar="DECKLIST", help="List decks in DECKLIST")
@click.option(
    "/list",
    "list_games",
    metavar="PAGE",
    type=int,
    is_flag=False,
    flag_value=1,
    help="List games page",
)
@click.option(
    "/join",
    "join_game",
    type=click.Choice(("corp", "runner", "spectate")),
    help="Join game identified by the /game option",
)
@click.option(
    "/game",
    "game_id",
    metavar="GAME_ID",
    callback=parse_game_id,
    help="Game id is `SEQ[:POOL]` where the optional POOL defaults to todays pool.",
)
@click.option("/new", "new_game", type=click.Choice(("corp", "runner")), help="Create new game")
@command_argument
@click.pass_obj
async def lobby_cmd(
    lobby, nick, whoami, list_decks, list_games, join_game, game_id, new_game, command
):
    if nick:
        await lobby.client_info.setNick(nick=nick).a_wait()
        click.echo("nick name changed")

    if whoami:
        nick = (await lobby.client_info.getNick().a_wait()).nick
        click.echo(f"you are known as {nick!r}")

    if list_decks:
        decks = (await lobby.root.listDecks(decklist=list_decks).a_wait()).decks
        for deck in decks:
            click.echo(f"== {deck.name}")
            for entry in deck.cards:
                click.echo(f" - {entry.count}x {entry.card.name}")

    if join_game:
        logging.info(f"join game: {game_id} as {join_game}")
        player = (await lobby.root.joinGame(role=join_game, gameId=game_id).a_wait()).player
        click.echo(f"joined game {await player.getInfo().a_wait()}")
        if not command:
            command = "game"

    if new_game:
        player = (await lobby.root.newGame(role=new_game).a_wait()).player
        click.echo(f"created game for {await player.getInfo().a_wait()}")
        if not command:
            command = "game"

    if list_games:
        res = await lobby.root.listGames(page=list_games, pageSize=PAGE_SIZE).a_wait()
        if not res.totalCount:
            click.echo("there are no games")
        else:
            pages = math.ceil(res.totalCount / PAGE_SIZE)
            for game in res.games:
                click.echo(f"  - game: {game}")
            click.echo(f"  // page {list_games}/{pages} || {res.totalCount} games in total")

    lobby.switch_cmd(command)


@cli_command("game")
@command_argument
@click.pass_obj
async def game_cmd(lobby, command):
    click.echo(f"Game cmd: {lobby}")
    lobby.switch_cmd(command)
