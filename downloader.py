from asyncio import sleep
from .. import loader, utils
from requests import get
import io
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl
import os
# Author: https://t.me/ftgmodulesbyfl1yd

def register(cb):
    cb(ReplyDownloaderMod())


class ReplyDownloaderMod(loader.Module):
    strings = {'name': 'Reply Downloader'}

    async def dlrcmd(self, message):
        name = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if reply:
            await message.edit('Downloading...')
            if reply.text:
                text = reply.text
                fname = f'{name or str(message.id + reply.id)}.txt'
                file = open(fname, 'w')
                file.write(text)
                file.close()
                await message.edit(
                    f'File saved as <code>{fname}</code>.\nGet this file <code>.ulr {fname}</code>.')
            else:
                ext = reply.file.ext
                fname = f'{name or str(message.id + reply.id)}{ext}'
                await message.client.download_media(reply, fname)
                await message.edit(
                    f'File saved as <code>{fname}</code>.\nGet this file <code>.ulr {fname}</code>.')
        else:
            return await message.edit('Please reply to message')

    async def ulrcmd(self, message):
        name = utils.get_args_raw(message)
        d = False
        if ('d ' in name):
            d = True
        if name:
            try:
                name = name.replace('d ', '')
                await message.edit(f'Sending <code>{name}</code>...')
                if d == True:
                    await message.client.send_file(message.to_id, f'{name}')
                    await message.edit(f'Sending <code>{name}</code>... \nDeleting <code>{name}</code>...')
                    os.remove(name)
                    await message.edit(
                        f'Sending <code>{name}</code>... \nDeleting <code>{name}</code>...')
                    await sleep(0.5)
                else:
                    await message.client.send_file(message.to_id, name)
            except:
                return await message.edit('File does not exist')
            await message.delete()
        else:
            return await message.edit('No arguments')

    async def urldlcmd(self, message):
        event = message
        args = utils.get_args_raw(event)
        reply = await event.get_reply_message()
        if not args:
            if not reply:
                await event.edit("<b>Ссылки нету!</b>")
                return
            message = reply
        else:
            message = event

        if not message.entities:
            await event.edit("<b>Ссылки нету!</b>")
            return

        urls = []
        for ent in message.entities:
            if type(ent) in [MessageEntityUrl, MessageEntityTextUrl]:
                url_ = True
                if type(ent) == MessageEntityUrl:
                    offset = ent.offset
                    length = ent.length
                    url = message.raw_text[offset:offset + length]
                else:
                    url = ent.url
                if not url.startswith("http"):
                    url = "http://" + url
                urls.append(url)

        if not urls:
            await event.edit("<b>Ссылки нету!</b>")
            return
        for url in urls:
            try:
                await event.edit("Downloading...")
                fname = url.split("/")[-1]
                text = get(url, stream=False)
                file = io.BytesIO(text.content)
                file.name = fname
                file.seek(0)
                await event.edit("<b>Sending...</b>\n" + url)
                await event.client.send_file(event.to_id, file, reply_to=reply)

            except Exception as e:
                await event.reply("<b>Ошибка при загрузке!</b>\n" + url + "\n<code>" + str(e) + "</code>")

        await event.delete()

