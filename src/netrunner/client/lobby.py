from __future__ import annotations

from dataclasses import dataclass

import click
from netrunner.util import cli_command

from netrunner import api

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
@click.option("/list", "list_games", type=int, help="List games page")
@click.option("/new", "new_game", help="Create new game", type=click.Choice(("corp", "runner")))
@command_argument
@click.pass_obj
async def lobby_cmd(lobby, nick, whoami, list_games, new_game, command):
    lobby.switch_cmd(command)

    if nick:
        await lobby.client_info.setNick(nick=nick).a_wait()
        click.echo("nick name changed")

    if whoami:
        nick = (await lobby.client_info.getNick().a_wait()).nick
        click.echo(f"you are known as {nick!r}")

    if new_game:
        player = (await lobby.root.newGame(role=new_game).a_wait()).player
        click.echo(f"created game for {await player.getInfo().a_wait()}")
        if not command:
            lobby.switch_cmd("game")

    if list_games:
        res = await lobby.root.listGames(page=list_games).a_wait()
        for game in res.games:
            players = await game.getPlayers().a_wait()
            click.echo(f" - game: corp={players.corp_nick}, runner={players.runner_nick}")
        click.echo(f" = {res.totalCount} games in total")


@cli_command("game")
@command_argument
@click.pass_obj
async def game_cmd(lobby, command):
    click.echo(f"Game cmd: {lobby}")
    lobby.switch_cmd(command)
