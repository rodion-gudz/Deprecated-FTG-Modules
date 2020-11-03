from .. import loader, utils  # pylint: disable=relative-beyond-top-level
import logging
from requests import post
import io
from .. import loader, utils
import asyncio
import requests
from telethon.tl.types import DocumentAttributeFilename

# Author: https://t.me/GovnoCodules

logger = logging.getLogger(__name__)


@loader.tds
class x0Mod(loader.Module):
    strings = {
        "name": "File uploader"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.sudo
    async def x0cmd(self, message):
        await message.edit("<b>Uploading...</b>")
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("<b>Reply to message</b>")
            return
        media = reply.media
        if not media:
            file = io.BytesIO(bytes(reply.raw_text, "utf-8"))
            file.name = "txt.txt"
        else:
            file = io.BytesIO(await self.client.download_file(media))
            file.name = reply.file.name if reply.file.name else reply.file.id + reply.file.ext
        try:
            x0at = post('https://x0.at', files={'file': file})
        except ConnectionError as e:
            await message.edit(ste(e))
            return
        url = x0at.text
        output = f'<a href="{url}">URL: </a><code>{url}</code>'
        await message.edit(output)

    async def phcmd(self, message):
        """.ph <reply photo or video>"""
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await message.edit("<b>Reply to photo or video/gif</b>")
                return
        else:
            await message.edit("<b>Reply to photo or video/gif</b>")
            return

        file = await message.client.download_media(data, bytes)
        path = requests.post('https://te.legra.ph/upload', files={'file': ('file', file, None)}).json()
        try:
            link = 'https://te.legra.ph' + path[0]['src']
        except KeyError:
            link = path["error"]
        await message.edit("<b>" + link + "</b>")


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.audio or reply_message.voice:
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False
    if not data or data is None:
        return False
    else:
        return data
