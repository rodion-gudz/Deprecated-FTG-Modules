from requests import post
from telethon.tl.types import DocumentAttributeFilename
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon import events
from .. import loader, utils
import io
from io import BytesIO
from PIL import Image
import logging
import requests
import asyncio

# Author: https://t.me/GovnoCodules

logger = logging.getLogger(__name__)

def sgen(agen, loop):
    while True:
        try:
            yield utils.run_async(loop, agen.__anext__())
        except StopAsyncIteration:
            return


@loader.tds
class x0Mod(loader.Module):
    strings = {
        "name": "File uploader",
        "up_cfg_doc": "URL to upload the file to.",
        "no_file": "<code>Provide a file to upload</code>",
        "uploading": "<code>Uploading...</code>",
        "uploaded": "<a href={}>Uploaded!</a>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig("UPLOAD_URL", "https://transfer.sh/{}",
                                          lambda m: self.strings("up_cfg_doc", m))
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
        output = f'{url}'
        await message.edit(output)

    async def phcmd(self, message):
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await message.edit("<b>Reply to photo or video/gif</b>")
                return
        else:
            await message.edit("<b>Reply to photo or video/gif</b>")
            return

        file = lol(await message.client.download_media(data, bytes))
        path = requests.post('https://te.legra.ph/upload', files={'file': ('file', file, None)}).json()
        try:
            link = 'https://te.legra.ph' + path[0]['src']
        except KeyError:
            link = path["error"]
        await message.edit("<b>" + link + "</b>")

    async def imgurcmd(self, event):
        chat = '@ImgUploadBot'
        reply = await event.get_reply_message()
        async with event.client.conversation(chat) as conv:

            if not reply:
                await event.edit("где реплай на медиа.")
                return
            else:
                pic = await check_mediaa(event, reply)
                if not pic:
                    await utils.answer(event, 'это не изображение, лол.')
                    return
            await event.edit("Uploading...")
            try:
                what = lol(pic)
                response = conv.wait_event(events.NewMessage(incoming=True, from_users=985223903))
                await event.client.send_file(chat, what)
                response = await response
            except YouBlockedUserError:
                await event.edit('<code>Разблокируй @imgurbot_bot</code>')
                return
            await event.edit(response.text)

    async def hastecmd(self, message):
        media = False
        reply_to = False
        user_msg = f"""{utils.get_args_raw(message)}"""
        reply = await message.get_reply_message()
        if reply:
            if reply.media:
                user_msg = reply.media
                media = True
                reply_to = True
            else:
                user_msg = f"""{reply.text}"""
                reply_to = True
        else:
            pass
        await message.edit('<code>Uploading...</code>')
        async with message.client.conversation('@hastebin_bbot') as conv:
            try:
                response = conv.wait_event(events.NewMessage(incoming=True,
                                                             from_users=1358418309))
                if media:
                    await message.client.send_file('@hastebin_bbot', user_msg)
                else:
                    await message.client.send_message('@hastebin_bbot', user_msg)
                response = await response
            except YouBlockedUserError:
                await message.reply('<code>Разблокируй </code> @hastebin_bbot')
                return
            await message.delete()
            if reply_to:
                await message.client.send_message(message.to_id, response.message, reply_to=reply.id)
            else:
                await message.client.send_message(message.to_id, response.message)

    async def uploadshcmd(self, message):
        if message.file:
            msg = message
        else:
            msg = (await message.get_reply_message())
        doc = getattr(msg, "media", None)
        if doc is None:
            await utils.answer(message, self.strings("no_file", message))
            return
        doc = message.client.iter_download(doc)
        logger.debug("begin transfer")
        await utils.answer(message, self.strings("uploading", message))
        r = await utils.run_sync(requests.put, self.config["UPLOAD_URL"].format(msg.file.name),
                                 data=sgen(doc, asyncio.get_event_loop()))
        logger.debug(r)
        r.raise_for_status()
        logger.debug(r.headers)
        await utils.answer(message, self.strings("uploaded", message).format(r.text))


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


def lol(reply):
    scrrrra = Image.open(BytesIO(reply))
    out = io.BytesIO()
    out.name = "outsider.png"
    scrrrra.save(out)
    return out.getvalue()


async def check_mediaa(message, reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.document:
            if reply.gif or reply.video or reply.audio or reply.voice:
                return None
            data = reply.media.document
        else:
            return None
    else:
        return None
    if not data or data is None:
        return None
    else:
        data = await message.client.download_file(data, bytes)
        try:
            Image.open(io.BytesIO(data))
            return data
        except:
            return None
