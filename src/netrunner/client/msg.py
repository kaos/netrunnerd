from __future__ import annotations

from netrunner.util import ainput

from netrunner.client.cmd import command


class send_msg(command):
    click_args = ("/msg",)
    click_kwargs = dict(metavar="NICK", help="Send private message to NICK.")

    async def do_invoke(self, send_msg: str, **kwargs):
        msg = await ainput(f"message for {send_msg}: ", split=False)
        if msg:
            await self.lobby.messages.send(send_msg, msg)
