from __future__ import annotations

import asyncio

import click

from netrunner import api
from netrunner.capnp.client import AsyncClient


@click.command("netrunner")
@click.option("--address", default="127.0.0.1")
@click.option("--port", type=int, default=7374)
def main(address, port):
    asyncio.run(client(address, port))


async def client(address, port):
    connection = await AsyncClient.connect(address, port, bootstrap_cls=api.schema.NetrunnerLobby)
    print(f"Conn: {connection}")
    lobby = connection.interface
    print(f"lobby: {lobby}")
    myself = await lobby.myself().a_wait()
    print(f"info: {myself} {myself.info}")
    print(f"nick: {await myself.info.getNick().a_wait()}")


if __name__ == "__main__":
    main()
