from .. import loader, utils
from requests import get
import io
import logging
import sys
import pygments
from pygments.lexers import Python3Lexer
from pygments.formatters import ImageFormatter
import os
logger = logging.getLogger(__name__)



@loader.tds
class WebShotMod(loader.Module):
    strings = {
        "name": "Screenshots"
    }

    async def client_ready(self, client, db):
        self.client = client

    def __init__(self):
        self.name = self.strings['name']

    @loader.sudo
    async def webshotcmd(self, message):
        reply = None
        link = utils.get_args_raw(message)
        if not link:
            reply = await message.get_reply_message()
            if not reply:
                await message.delete()
                return
            link = reply.raw_text
        await message.edit("<b>S c r e e n s h o t i n g . . .</b>")
        url = "https://webshot.deam.io/{}/?width=1920&height=1080?type=png"
        file = get(url.format(link))
        if not file.ok:
            await message.edit("<b>Something went wrong...</b>")
            return
        file = io.BytesIO(file.content)
        file.name = "webshot.png"
        file.seek(0)
        await message.client.send_file(message.to_id, file, reply_to=reply)
        await message.delete()

    async def pyshotcmd(self, message):
        message.edit("<b>Py to PNG</b>")
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("<b>reply to file.py</b>")
            return
        media = reply.media
        if not media:
            await message.edit("<b>reply to file.py</b>")
            return
        file = await message.client.download_file(media)
        text = file.decode('utf-8')
        pygments.highlight(text, Python3Lexer(), ImageFormatter(font_name='DejaVu Sans Mono', line_numbers=True),
                           'out.png')
        await message.client.send_file(message.to_id, 'out.png', force_document=True)
        os.remove("out.png")
        await message.delete()

