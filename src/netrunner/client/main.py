from __future__ import annotations

import asyncio
import atexit
import inspect
import os
import readline

import click

from netrunner import api
from netrunner.capnp.client import AsyncClient
from netrunner.client.lobby import NetrunnerLobby, lobby_cmd
from netrunner.util import ainput


@click.command("netrunner")
@click.option("--address", default="127.0.0.1")
@click.option("--port", type=int, default=7374)
@click.option("--history-file", default="~/.netrunner-history")
def main(address, port, history_file):
    if history_file:
        init_history(history_file)

    asyncio.run(client_connect(address, port))


def init_history(history_file: str) -> None:
    histfile = history_file.replace("~", os.path.expanduser("~"))
    try:
        readline.read_history_file(histfile)
        # default history len is -1 (infinite), which may grow unruly
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    atexit.register(readline.write_history_file, histfile)


async def client_connect(address, port):
    connection = await AsyncClient.connect(address, port, bootstrap_cls=api.schema.NetrunnerLobby)
    lobby = connection.interface
    myself = await lobby.myself().a_wait()
    coroutines = [run(NetrunnerLobby(root=lobby, client_info=myself.info))]
    tasks = asyncio.gather(*coroutines, return_exceptions=True)
    await tasks


async def run(lobby):
    cmd = lobby_cmd
    while True:
        args = await ainput(f"{cmd.name}> ")
        if not args:
            continue
        if args == ["q"]:
            break
        if args[0] == "help":
            args[0] = "--help"
        try:
            rc = cmd(prog_name=cmd.name, args=args, obj=lobby, standalone_mode=False)
            if inspect.isawaitable(rc):
                rc = await rc
        except Exception as e:
            click.echo(f"ERROR in {cmd.name}: {e}")


if __name__ == "__main__":
    main()
