from __future__ import annotations

import click

from netrunner.client.cmd import command


class nick(command):
    click_kwargs = dict(metavar="NAME", help="Change nick name")

    async def do_invoke(self, nick: str, **kwargs):
        await self.lobby.client_info.setNick(nick=nick).a_wait()
        click.echo(f"nick name changed to {nick}")


class whoami(command):
    click_kwargs = dict(is_flag=True, default=None, help="Check nick name")

    async def do_invoke(self, whoami: bool, **kwargs):
        nick = (await self.lobby.client_info.getNick().a_wait()).nick
        click.echo(f"you are known as {nick}")


class view_card(command):
    click_args = ("/card",)
    click_kwargs = dict(metavar="CODE", help="View info about card with a given card CODE.")

    async def do_invoke(self, view_card: str, **kwargs):
        card = (await self.lobby.root.viewCard(cardCode=view_card).a_wait()).card
        click.echo(f"{card}\n")


class online(command):
    click_kwargs = dict(is_flag=True, default=None, help="List online users.")

    async def do_invoke(self, **kwargs):
        users = (await self.lobby.root.online().a_wait()).users
        for user in users:
            click.echo(f" - {user}")
