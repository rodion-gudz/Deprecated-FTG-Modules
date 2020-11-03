import logging, os
from random import choice, randint

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class TgsKillerMod(loader.Module):
    strings = {"name": "Stickers distort"}

    @loader.unrestricted
    async def tgscmd(self, message):
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("Reply animated sticker")
            return
        if not reply.file:
            await message.edit("Reply animated sticker")
            return
        if not reply.file.name.endswith(".tgs"):
            await message.edit("Reply animated sticker")
            return
        await message.edit("Distorting...")
        await reply.download_media("tgs.tgs")
        os.system("lottie_convert.py tgs.tgs json.json")
        with open("json.json", "r") as f:
            stick = f.read()
            f.close()

        for i in range(1, randint(6, 10)):
            stick = choice([stick.replace(f'[{i}]', f'[{(i + i) * 3}]'), stick.replace(f'.{i}', f'.{i}{i}')])

        with open("json.json", "w") as f:
            f.write(stick)
            f.close()

        os.system("lottie_convert.py json.json tgs.tgs")
        await reply.reply(file="tgs.tgs")
        os.remove("tgs.tgs")
        os.remove("json.json")
        await message.delete()