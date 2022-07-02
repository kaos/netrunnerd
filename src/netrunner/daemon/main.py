from __future__ import annotations

import asyncio

import click

from netrunner.capnp.server import AsyncServer
from netrunner.daemon.lobby import NetrunnerLobbyImpl


@click.command("netrunnerd")
@click.option("--address", default="127.0.0.1")
@click.option("--port", type=int, default=7374)
def main(address, port):
    asyncio.run(AsyncServer.run(address, port, bootstrap_cls=NetrunnerLobbyImpl))


if __name__ == "__main__":
    main()
