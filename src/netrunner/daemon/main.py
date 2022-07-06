from __future__ import annotations

import asyncio

import click
from underpants.engine import RulesEngine

from netrunner.capnp.server import AsyncServer
from netrunner.daemon.lobby import NetrunnerLobbyImpl


@click.command(
    "netrunnerd",
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
)
@click.option("--address", default="127.0.0.1")
@click.option("--port", type=int, default=7374)
@click.option("--plugin", multiple=True, help="Load additional netrunner plugins.")
@click.pass_context
def main(ctx, address, port, plugin):
    NetrunnerLobbyImpl.engine = RulesEngine.create(
        "netrunnerd", args=ctx.args, backends=("netrunner.engine", *plugin)
    )
    with NetrunnerLobbyImpl.engine.pants_logging():
        asyncio.run(AsyncServer.run(address, port, bootstrap_cls=NetrunnerLobbyImpl))


if __name__ == "__main__":
    main()
