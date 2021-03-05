# -*- coding: utf-8 -*-

# Module author: @m4xx1m, @ftgmodulesbyfl1yd, @dekftgmodules

from PIL import Image
import logging
import os
from pydub import AudioSegment
from telethon import types
import io
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ConverterMod(loader.Module):
    """Converter module"""
    strings = {
        "name": "Converter"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.sudo
    async def wtpcmd(self, message):
        """WEBP to PNG"""
        reply_message = await message.get_reply_message()
        image = io.BytesIO()
        await self.client.download_media(reply_message.media.document, image)
        image = Image.open(image)
        image_stream = io.BytesIO()
        image_stream.name = "png.png"
        image.save(image_stream, "PNG")
        image_stream.seek(0)
        await self.client.delete_messages(message.to_id, message.id)
        await self.client.send_file(message.to_id, image_stream,
                                    force_document=True)

    @loader.sudo
    async def ptwcmd(self, message):
        """PNG to WEBP"""
        reply_message = await message.get_reply_message()
        image = io.BytesIO()
        await self.client.download_media(reply_message.media, image)
        image = Image.open(image)
        image_stream = io.BytesIO()
        image_stream.name = "webp.webp"
        image.save(image_stream, "WEBP")
        image_stream.seek(0)
        await self.client.delete_messages(message.to_id, message.id)
        await self.client.send_file(message.to_id, image_stream,
                                    force_document=False)

    @loader.sudo
    async def jtpcmd(self, message):
        """JPG to PNG"""
        reply_message = await message.get_reply_message()
        image = io.BytesIO()
        await self.client.download_media(reply_message.media, image)
        image = Image.open(image).convert("RGB")
        image_stream = io.BytesIO()
        image_stream.name = "10_из_10шакалов.png"
        image.save(image_stream, "PNG")
        image_stream.seek(0)
        await self.client.delete_messages(message.to_id, message.id)
        await self.client.send_file(message.to_id, image_stream,
                                    force_document=True)

    async def togifcmd(self, message):
        """Сделать из медиа гифку.\nИспользование: .togif <реплай>."""
        try:
            await message.edit("Скачиваем...")
            reply = await message.get_reply_message()
            if reply:
                if reply.video:
                    await message.client.download_media(reply.media,
                                                        "inputfile.mp4")
                    await message.edit("Конвертируем...")
                    os.system(
                        "ffmpeg -i inputfile.mp4 -vcodec copy -an outputfile.mp4")
                    await message.edit("Отправляем...")
                    await message.client.send_file(message.to_id,
                                                   "outputfile.mp4")
                elif reply.file.ext == ".tgs":
                    await message.client.download_media(reply.media, f"tgs.tgs")
                    await message.edit("Конвертируем...")
                    os.system("lottie_convert.py tgs.tgs tgs.gif")
                    await message.edit("Отправляем...")
                    await message.client.send_file(message.to_id, "tgs.gif",
                                                   reply_to=reply.id)
                else:
                    return await message.edit("Этот файл не поддерживается.")
                await message.delete()
                os.system("rm -rf inputfile.mp4 outputfile.mp4 tgs.tgs tgs.gif")
            else:
                return await message.edit("Нет реплая на видео/гиф/стикр.")
        except:
            await message.edit("Произошла непредвиденная ошибка.")
            os.system("rm -rf inputfile.mp4 outputfile.mp4 tgs.tgs tgs.gif")
            return

    async def mp3cmd(self, message):
        """.mp3 <reply to audio>
                    Сконвертировать войс в mp3
                """
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
        await message.client.send_file(message.to_id, m, reply_to=reply.id,
                                       attributes=[
                                           types.DocumentAttributeAudio(
                                               duration=
                                               reply.document.attributes[
                                                   0].duration,
                                               title=f"Converted to " + formatik,
                                               performer="Converter")])
        await message.delete()

    async def oggcmd(self, message):
        """.ogg <reply to audio>
                    Сконвертировать войс в ogg
                """
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
        await message.client.send_file(message.to_id, m, reply_to=reply.id,
                                       attributes=[
                                           types.DocumentAttributeAudio(
                                               duration=
                                               reply.document.attributes[
                                                   0].duration,
                                               title=f"Converted to " + formatik,
                                               performer="Converter")])
        await message.delete()

    async def tovoicecmd(self, message):
        """.tovoice <reply to audio>
            Сконвертировать аудио в войс
        """
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        else:
            try:
                if reply.media.document.attributes[0].voice == True:
                    await message.edit("Это войс, а не аудиофайл!")
                    return
            except:
                await message.edit("Это не аудиофайл!")
                return
        await message.edit("Скачиваем...")
        au = io.BytesIO()
        await message.client.download_media(reply.media.document, au)
        au.seek(0)
        await message.edit("Делаем войс...")
        audio = AudioSegment.from_file(au)
        m = io.BytesIO()
        m.name = "voice.ogg"
        audio.split_to_mono()
        await message.edit("Экспортируем...")
        dur = len(audio) / 1000
        audio.export(m, format="ogg", bitrate="64k", codec="libopus")
        await message.edit("Отправляем...")
        m.seek(0)
        await message.client.send_file(message.to_id, m, reply_to=reply.id,
                                       voice_note=True, duration=dur)
        await message.delete()