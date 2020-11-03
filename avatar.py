
import logging
import os
from .. import loader, utils
from telethon import functions
logger = logging.getLogger(__name__)


class GetPPMod(loader.Module):
    strings = {"name": "Avatar utils"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def potocmd(self, message):
        id = utils.get_args_raw(message)
        user = await message.get_reply_message()
        chat = message.input_chat
        if user:
            photos = await self.client.get_profile_photos(user.sender)
            u = True
        else:
            photos = await self.client.get_profile_photos(chat)
            u = False
        if id.strip() == "":
            if len(photos) > 0:
                await self.client.send_file(message.chat_id, photos)
            else:
                try:
                    if u is True:
                        photo = await self.client.download_profile_photo(user.sender)
                    else:
                        photo = await self.client.download_profile_photo(message.input_chat)
                    await self.client.send_file(message.chat_id, photo)
                except:
                    await message.edit("<code>This user has no photos</code>")
                    return
        else:
            try:
                id = int(id)
                if id <= 0:
                    await message.edit("<code>ID number you entered is invalid</code>")
                    return
            except:
                 await message.edit("<code>ID number you entered is invalid</code>")
                 return
            if int(id) <= (len(photos)):
                send_photos = await self.client.download_media(photos[id - 1])
                await self.client.send_file(message.chat_id, send_photos)
            else:
                await message.edit("<code>No photo found with that id</code>")
                return
        await message.delete()

    async def onavacmd(self, message):
        try:
            reply = await message.get_reply_message()
            if reply:
                await message.edit("Скачиваем...")
                if reply.video:
                    await message.client.download_media(reply.media, "ava.mp4")
                    await message.edit("Конвертируем...")
                    os.system("ffmpeg -i ava.mp4 -c copy -an gifavaa.mp4 -y")
                    os.system("ffmpeg -i gifavaa.mp4 -vf scale=360:360 gifava.mp4 -y")
                else:
                    await message.client.download_media(reply.media, "tgs.tgs")
                    await message.edit("Конвертируем...")
                    os.system("lottie_convert.py tgs.tgs tgs.gif; mv tgs.gif gifava.mp4")
            else:
                return await message.edit("Нет реплая на гиф/анимированный стикер/видеосообщение.")
            await message.edit("Устанавливаем аву...")
            await message.client(
                functions.photos.UploadProfilePhotoRequest(video=await message.client.upload_file("gifava.mp4"),
                                                           video_start_ts=0.0))
            await message.edit("Ава установлена.")
            os.system("rm -rf ava.mp4 gifava.mp4 gifavaa.mp4 tgs*")
        except:
            await message.edit(
                "Блин, какой я дурак, я не отличаю гифку/анимированный стикер/видео от любого другого файла.\n\n"
                "<b>ЭТОТ ФАЙЛ НЕ ПОДДЕРЖИВАЕТСЯ!!!</b>(либо просто какая-то тех.ошибка c: )")
            try:
                os.system("rm -rf ava.mp4 gifava.mp4 gifavaa.mp4 tgs*")
            except:
                pass
            return

