import io, random, glob, os
from PIL import Image
from telethon.tl.types import DocumentAttributeFilename
from .. import loader, utils
from .. import loader, utils  # pylint: disable=relative-beyond-top-level
import io
from PIL import Image, ImageOps
from telethon.tl.types import DocumentAttributeFilename
import logging
import random

# Author: https://t.me/GovnoCodules

@loader.tds
class DistortMod(loader.Module):
    strings = {"name": "Photo editing"}
    async def distortcmd(self, message):
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await message.edit("Error")
                return
        else:
            await message.edit("Error")
            return
        await message.edit("Distorting...")
        for distorted in glob.glob("distorted*"):
            os.remove(distorted)
        for findistorted in glob.glob("*/distorted*"):
            os.remove(findistorted)

        fname = f"distorted{random.randint(1, 100)}.png"

        with open(fname, "wb") as file:
            file.write(await message.client.download_media(data, bytes))
        image = Image.open(fname)
        image.save(fname)
        imgdimens = image.width, image.height
        distortcmd = f"convert {fname} -liquid-rescale 60x60%! -resize {imgdimens[0]}x{imgdimens[1]}\! {fname}"
        os.system(distortcmd)
        image = Image.open(f"{fname}")
        buf = io.BytesIO()
        buf.name = 'image.png'
        image.save(buf, 'PNG')
        buf.seek(0)
        await message.edit("Sending...")
        await message.client.send_file(message.chat_id, buf, reply_to=reply_message.id)
        await message.delete()

    async def soapcmd(self, message):
        soap = 3
        a = utils.get_args(message)
        if a:
            if a[0].isdigit():
                soap = int(a[0])
                if soap <= 0:
                    soap = 3

        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await utils.answer(message, "<code>Reply to pic or stick!</code>")
                return
        else:
            await utils.answer(message, "<code>Reply to pic or stick!</code>")
            return

        await message.edit("Soaping...")
        file = await self.client.download_media(data, bytes)
        media = await Soaping(file, soap)
        await message.delete()

        await message.client.send_file(message.to_id, media)


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.gif or reply_message.video or reply_message.audio or reply_message.voice:
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


async def Soaping(file, soap):
    img = Image.open(io.BytesIO(file))
    (x, y) = img.size
    img = img.resize((x // soap, y // soap), Image.ANTIALIAS)
    img = img.resize((x, y))
    soap_io = io.BytesIO()
    soap_io.name = "image.jpeg"
    img = img.convert("RGB")
    img.save(soap_io, "JPEG", quality=100)
    soap_io.seek(0)
    return soap_io

