from __future__ import annotations

from dataclasses import dataclass

import click

from netrunner import api
from netrunner.util import cli_command

command_argument = click.argument(
    "command",
    nargs=1,
    required=False,
    type=click.Choice(cli_command.command_names),
)


@dataclass
class NetrunnerLobby:
    root: api.schema.NetrunnerLobby  # type: ignore[name-defined]
    client_info: api.schema.ClientInfo  # type: ignore[name-defined]
    cmd: click.Command

    def switch_cmd(self, command: str) -> None:
        if not command:
            return
        self.cmd = cli_command.registry[command]


@cli_command("lobby")
@click.option("/nick", help="Change nick name")
@click.option("/whoami", is_flag=True, help="Check nick name")
@command_argument
@click.pass_obj
async def lobby_cmd(lobby, nick, whoami, command):
    click.echo(f"Lobby cmd: {lobby}")
    lobby.switch_cmd(command)

    if nick:
        await lobby.client_info.setNick(nick=nick).a_wait()
        click.echo("nick name changed")

    if whoami:
        nick = (await lobby.client_info.getNick().a_wait()).nick
        click.echo(f"you are known as {nick!r}")


@cli_command("game")
@command_argument
@click.pass_obj
async def game_cmd(lobby, command):
    click.echo(f"Game cmd: {lobby}")
    lobby.switch_cmd(command)
