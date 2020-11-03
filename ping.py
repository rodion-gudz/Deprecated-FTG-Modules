from telethon import events
from datetime import datetime
from uniborg.util import admin_cmd
from .. import loader, utils
from time import sleep

logger = logging.getLogger(__name__)

@borg.on(admin_cmd("ping"))
class PingMod(loader.Module):
    strings = {"name": "Ping"}

    async def _(self):
        if self.fwd_from:
            return
        start = datetime.now()
        await self.edit("`Ping checking...`")
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        sleep(0.5)
        await self.edit("**Ping:** `{}ms`".format(ms))