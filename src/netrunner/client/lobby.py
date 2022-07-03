from __future__ import annotations

from dataclasses import dataclass

import click

from netrunner import api


@dataclass(frozen=True)
class NetrunnerLobby:
    root: api.schema.NetrunnerLobby  # type: ignore[name-defined]
    client_info: api.schema.ClientInfo  # type: ignore[name-defined]


@click.command("lobby")
@click.option("/nick", help="Change nick name")
@click.option("/whoami", is_flag=True, help="Check nick name")
@click.pass_obj
async def lobby_cmd(lobby, nick, whoami):
    click.echo(f"Lobby cmd: {lobby}")

    if nick:
        await lobby.client_info.setNick(nick=nick).a_wait()

    if whoami:
        nick = (await lobby.client_info.getNick().a_wait()).nick
        click.echo(f"nick name: {nick}")
