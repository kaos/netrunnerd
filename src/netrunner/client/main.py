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
from netrunner.client.cmd import command, select_mode
from netrunner.client.deck import list_decks
from netrunner.client.game import join_game, list_games, new_game
from netrunner.client.info import nick, view_card, whoami
from netrunner.client.lobby import NetrunnerLobby
from netrunner.client.mode import mode
from netrunner.util import ainput


@mode("lobby")
@nick.command()
@whoami.command()
@list_decks.command()
@list_games.command()
@join_game.command()
@new_game.command()
@view_card.command()
@select_mode.command()
async def mode_lobby(lobby, **kwargs):
    await command(lobby).invoke(**kwargs)


@mode("game")
@select_mode.command()
async def mode_game(lobby, **kwargs):
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
        args = await ainput(f"#{lobby.cmd.name} $ ")
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
        click.echo(f"ERROR in {lobby.cmd.name}: {e}\n\nTry /help for usage.\n")


if __name__ == "__main__":
    main()
