from PIL import Image, ImageOps
import logging
import os
from pydub import AudioSegment
from .. import loader, utils
from telethon import types
import io
logger = logging.getLogger(__name__)


def register(cb):
    cb(WEBPtoPNGMod())


@loader.tds
class WEBPtoPNGMod(loader.Module):
    strings = {
        "name": "Converter"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.sudo
    async def pngcmd(self, message):
        reply_message = await message.get_reply_message()
        image = io.BytesIO()
        await self.client.download_media(reply_message.media.document, image)
        image = Image.open(image)
        image_stream = io.BytesIO()
        image_stream.name = "png.png"
        image.save(image_stream, "PNG")
        image_stream.seek(0)
        await self.client.delete_messages(message.to_id, message.id)
        await self.client.send_file(message.to_id, image_stream, force_document=True)

    async def jpegcmd(self, message):
        reply_message = await message.get_reply_message()
        image = io.BytesIO()
        await self.client.download_media(reply_message.media.document, image)
        image = Image.open(image).convert("RGB")
        image_stream = io.BytesIO()
        image_stream.name = "jpeg.jpeg"
        image.save(image_stream, "JPEG")
        image_stream.seek(0)
        await self.client.delete_messages(message.to_id, message.id)
        await self.client.send_file(message.to_id, image_stream)

    async def webpcmd(self, message):
        reply_message = await message.get_reply_message()
        image = io.BytesIO()
        await self.client.download_media(reply_message.media, image)
        image = Image.open(image)
        image_stream = io.BytesIO()
        image_stream.name = "webp.webp"
        image.save(image_stream, "WEBP")
        image_stream.seek(0)
        await self.client.delete_messages(message.to_id, message.id)
        await self.client.send_file(message.to_id, image_stream, force_document=False)

    async def gifcmd(self, message):
        try:
            await message.edit("Downloading...")
            reply = await message.get_reply_message()
            if reply:
                await message.edit("Converting...")
                await message.client.download_media(reply.media, "tgs.tgs")
                os.system("lottie_convert.py tgs.tgs tgs.gif")
                await message.edit("Sending...")
                await message.client.send_file(message.to_id, "tgs.gif")
                await message.delete()
                try:
                    os.remove("tgs*")
                except FileNotFoundError:
                    pass
            else:
                return await message.edit("Reply to media")
        except:
            await message.edit("Reply to media")
            try:
                os.remove("tgs*")
            except FileNotFoundError:
                pass
            return

    async def mp3cmd(self, message):
        reply = await message.get_reply_message()
        formatik = 'mp3'
        await message.edit("Downloading...")
        au = io.BytesIO()
        await message.client.download_media(reply.media.document, au)
        au.seek(0)
        await message.edit(f"Converting в {formatik}...")
        audio = AudioSegment.from_file(au)
        m = io.BytesIO()
        m.name = "Converted_to." + formatik
        audio.split_to_mono()
        await message.edit("Sending...")
        audio.export(m, format=formatik)
        m.seek(0)
        await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
            types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration,
                                         title=f"Converted to " + formatik, performer="Converter")])
        await message.delete()
    async def m4acmd(self, message):
        reply = await message.get_reply_message()
        formatik = 'm4a'
        await message.edit("Downloading...")
        au = io.BytesIO()
        await message.client.download_media(reply.media.document, au)
        au.seek(0)
        await message.edit(f"Converting в {formatik}...")
        audio = AudioSegment.from_file(au)
        m = io.BytesIO()
        m.name = "Converted_to." + formatik
        audio.split_to_mono()
        await message.edit("Sending...")
        audio.export(m, format=formatik)
        m.seek(0)
        await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
            types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration,
                                         title=f"Converted to " + formatik, performer="Converter")])
        await message.delete()
    async def oggcmd(self, message):
        reply = await message.get_reply_message()
        formatik = 'ogg'
        await message.edit("Downloading...")
        au = io.BytesIO()
        await message.client.download_media(reply.media.document, au)
        au.seek(0)
        await message.edit(f"Converting в {formatik}...")
        audio = AudioSegment.from_file(au)
        m = io.BytesIO()
        m.name = "Converted_to." + formatik
        audio.split_to_mono()
        await message.edit("Sending...")
        audio.export(m, format=formatik)
        m.seek(0)
        await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
            types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration,
                                         title=f"Converted to " + formatik, performer="Converter")])
        await message.delete()

