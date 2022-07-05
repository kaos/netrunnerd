from __future__ import annotations

import asyncio
import atexit
import inspect
import logging
import os
import readline

import click

from netrunner import api
from netrunner.capnp.client import AsyncClient
from netrunner.client.cmd import command, mode as select_mode
from netrunner.client.info import nick
from netrunner.client.lobby import NetrunnerLobby
from netrunner.client.mode import mode
from netrunner.util import ainput

logger = logging.getLogger(__name__)
PAGE_SIZE = 25


@mode("lobby")
@nick.command
@select_mode.command
# @click.option("/whoami", is_flag=True, help="Check nick name")
# @click.option("/decks", "list_decks", metavar="DECKLIST", help="List decks in DECKLIST")
# @click.option(
#     "/list",
#     "list_games",
#     metavar="PAGE",
#     type=int,
#     is_flag=False,
#     flag_value=1,
#     help="List games page",
# )
# @click.option(
#     "/join",
#     "join_game",
#     type=click.Choice(("corp", "runner", "spectate")),
#     help="Join game identified by the /game option",
# )
# @click.option(
#     "/game",
#     "game_id",
#     metavar="GAME_ID",
#     callback=parse_game_id,
#     help="Game id is `SEQ[:POOL]` where the optional POOL defaults to todays pool.",
# )
# @click.option("/new", "new_game", type=click.Choice(("corp", "runner")), help="Create new game")
async def mode_lobby(lobby, **kwargs):
    await command(lobby).invoke(**kwargs)

    # if nick:
    #     await lobby.client_info.setNick(nick=nick).a_wait()
    #     click.echo("nick name changed")

    # if whoami:
    #     nick = (await lobby.client_info.getNick().a_wait()).nick
    #     click.echo(f"you are known as {nick!r}")

    # if list_decks:
    #     decks = (await lobby.root.listDecks(decklist=list_decks).a_wait()).decks
    #     for deck in decks:
    #         click.echo(f"== {deck.name}")
    #         for entry in deck.cards:
    #             click.echo(f" - {entry.count}x {entry.card.name}")

    # if join_game:
    #     logging.info(f"join game: {game_id} as {join_game}")
    #     player = (await lobby.root.joinGame(role=join_game, gameId=game_id).a_wait()).player
    #     click.echo(f"joined game {await player.getInfo().a_wait()}")
    #     if not command:
    #         command = "game"

    # if new_game:
    #     player = (await lobby.root.newGame(role=new_game).a_wait()).player
    #     click.echo(f"created game for {await player.getInfo().a_wait()}")
    #     if not command:
    #         command = "game"

    # if list_games:
    #     res = await lobby.root.listGames(page=list_games, pageSize=PAGE_SIZE).a_wait()
    #     if not res.totalCount:
    #         click.echo("there are no games")
    #     else:
    #         pages = math.ceil(res.totalCount / PAGE_SIZE)
    #         for game in res.games:
    #             click.echo(f"  - game: {game}")
    #         click.echo(f"  // page {list_games}/{pages} || {res.totalCount} games in total")

    # lobby.switch_cmd(command)


@mode("game")
@select_mode.command
async def mode_game(lobby, **kwargs):
    click.echo(f"Game mode: {lobby}")
    await command(lobby).invoke(**kwargs)


@click.command("netrunner")
@click.option("--address", default="127.0.0.1")
@click.option("--port", type=int, default=7374)
@click.option("--history-file", default="~/.netrunner-history")
@click.option("--nick")
def main(address, port, history_file, nick):
    logging.basicConfig()

    if history_file:
        init_history(history_file)

    init_args = []
    if nick:
        init_args.append(("/nick", nick))

    asyncio.run(client_connect(address, port, init_args))


def init_history(history_file: str) -> None:
    histfile = history_file.replace("~", os.path.expanduser("~"))
    try:
        readline.read_history_file(histfile)
        # default history len is -1 (infinite), which may grow unruly
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    atexit.register(readline.write_history_file, histfile)


async def client_connect(address, port, init_args):
    click.echo(f"netrunner client connecting to {address}:{port}...")
    connection = await AsyncClient.connect(address, port, bootstrap_cls=api.schema.NetrunnerLobby)
    root = connection.interface
    myself = await root.myself().a_wait()
    lobby = NetrunnerLobby(root=root, client_info=myself.info, cmd=mode_lobby)
    for args in init_args:
        await apply_args(lobby, args)
    coroutines = [run(lobby)]
    tasks = asyncio.gather(*coroutines, return_exceptions=True)
    await tasks


async def run(lobby):
    while True:
        args = await ainput(f"\n#{lobby.cmd.name} $ ")
        if not args:
            continue
        if args == ["q"]:
            break

        await apply_args(lobby, args)


async def apply_args(lobby, args):
    try:
        res = lobby.cmd(prog_name=lobby.cmd.name, args=args, obj=lobby, standalone_mode=False)
        if inspect.isawaitable(res):
            await res
    except Exception as e:
        click.echo(f"ERROR in {lobby.cmd.name}: {e}\n\nTry /help for usage.")


if __name__ == "__main__":
    main()
