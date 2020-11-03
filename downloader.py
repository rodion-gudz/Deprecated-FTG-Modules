import os
from .. import loader, utils
from asyncio import sleep


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
        """Команда .ulr <d>* <название файла> отправляет файл в чат.\n* - удалить файл после отправки."""
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

