from .. import loader, utils
import logging
import requests

logger = logging.getLogger(__name__)


def register(cb):
    cb(WWWTrMod())


@loader.tds
class WWWTrMod(loader.Module):
    strings = {"name": "Weather"}

    async def client_ready(self, client, db):
        self.client = client

    @loader.sudo
    async def wcmd(self, message):
        city = utils.get_args(message)
        msg = []
        await message.edit("Processing...")
        for i in city:
            r = requests.get(
                "https://wttr.in/" + i + "?format=%l:+%c+%t,+%w+%m"
            )
            msg.append(r.text)
        await message.edit("".join(msg))

    async def pwcmd(self, message):
        args = utils.get_args_raw(message)
        city = args.replace(' ', '+')
        city = f"https://wttr.in/{city if city != None else ''}.png"
        await message.client.send_file(message.to_id, city)
        await message.delete()

    async def awcmd(self, message):
        city = utils.get_args_raw(message)
        await message.edit("Processing...")
        r = requests.get(f"https://wttr.in/{city if city != None else ''}?0?q?T&lang=ru")
        await message.edit(f"<code>Город: {r.text}</code>")
