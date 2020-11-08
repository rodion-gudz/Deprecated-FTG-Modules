from asyncio import sleep
from .. import loader, utils
from requests import get
import io
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl
import os
import os
import time
import asyncio
from requests import get
import requests
from .. import loader, utils
import io
from youtube_dl import YoutubeDL
from youtube_dl.utils import (DownloadError, ContentTooShortError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)
from asyncio import sleep
from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, YOUTUBE_API_KEY, CHROME_DRIVER, GOOGLE_CHROME_BIN
from userbot.events import register
from telethon.tl.types import DocumentAttributeAudio
from uniborg.util import progress, humanbytes, time_formatter
# Author: https://t.me/ftgmodulesbyfl1yd

def register(cb):
    cb(ReplyDownloaderMod())


class ReplyDownloaderMod(loader.Module):
    strings = {'name': 'Downloader'}

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

    async def dltiktokcmd(self, event):
        args = utils.get_args_raw(event)
        reply = await event.get_reply_message()
        if not args:
            if not reply:
                await event.edit("где ссылка, клоун.")
                return
            else:
                args = reply.raw_text
        await event.edit("Downloading...")
        data = {'url': args}
        response = requests.post('https://tik.fail/api/geturl', data=data).json()
        tik = requests.get(response['direct'])
        file = io.BytesIO(tik.content)
        file.name = response['direct']
        file.seek(0)
        await event.client.send_file(event.to_id, file)
        await event.delete()

    async def dlfilecmd(self, message):
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

    async def dlvideocmd(self, message):
        url = utils.get_args_raw(message)

        await message.edit("Preparing to download...")

        opts = {
            'format':
                'best',
            'addmetadata':
                True,
            'key':
                'FFmpegMetadata',
            'prefer_ffmpeg':
                True,
            'geo_bypass':
                True,
            'nocheckcertificate':
                True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'outtmpl':
                '%(id)s.mp4',
            'logtostderr':
                False,
            'quiet':
                True
        }

        try:
            await message.edit("`Fetching data, please wait..`")
            with YoutubeDL(opts) as rip:
                rip_data = rip.extract_info(url)
        except DownloadError as DE:
            await message.edit(f"`{str(DE)}`")
            return
        except ContentTooShortError:
            await message.edit("`The download content was too short.`")
            return
        except GeoRestrictedError:
            await message.edit(
                "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
            )
            return
        except MaxDownloadsReached:
            await message.edit("`Max-downloads limit has been reached.`")
            return
        except PostProcessingError:
            await message.edit("`There was an error during post processing.`")
            return
        except UnavailableVideoError:
            await message.edit("`Media is not available in the requested format.`")
            return
        except XAttrMetadataError as XAME:
            await message.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
            return
        except ExtractorError:
            await message.edit("`There was an error during info extraction.`")
            return
        except Exception as e:
            await message.edit(f"{str(type(e)): {str(e)}}")
            return
        c_time = time.time()
        await message.edit(f"Preparing to upload video:\
        \n**{rip_data['title']}**\
        \nby *{rip_data['uploader']}*")
        await message.client.send_file(
            message.chat_id,
            f"{rip_data['id']}.mp4",
            supports_streaming=True,
            caption=rip_data['title'],
            progress_callback=lambda d, t: asyncio.get_event_loop(
               ).create_task(
                   progress(d, t, message, c_time, "Uploading..",
                        f"{rip_data['title']}.mp4")))
        os.remove(f"{rip_data['id']}.mp4")
        await message.delete()

    async def dlaudiocmd(self, message):
        url = utils.get_args_raw(message)
        await message.edit("Preparing to download...")

        opts = {
            'format':
                'bestaudio',
            'addmetadata':
                True,
            'key':
                'FFmpegMetadata',
            'writethumbnail':
                True,
            'prefer_ffmpeg':
                True,
            'geo_bypass':
                True,
            'nocheckcertificate':
                True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl':
                '%(id)s.mp3',
            'quiet':
                True,
            'logtostderr':
                False
        }
        video = False
        song = True

        try:
            await message.edit("`Fetching data, please wait..`")
            with YoutubeDL(opts) as rip:
                rip_data = rip.extract_info(url)
        except DownloadError as DE:
            await message.edit(f"`{str(DE)}`")
            return
        except ContentTooShortError:
            await message.edit("`The download content was too short.`")
            return
        except GeoRestrictedError:
            await message.edit(
                "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
            )
            return
        except MaxDownloadsReached:
            await message.edit("`Max-downloads limit has been reached.`")
            return
        except PostProcessingError:
            await message.edit("`There was an error during post processing.`")
            return
        except UnavailableVideoError:
            await message.edit("`Media is not available in the requested format.`")
            return
        except XAttrMetadataError as XAME:
            await message.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
            return
        except ExtractorError:
            await message.edit("`There was an error during info extraction.`")
            return
        except Exception as e:
            await message.edit(f"{str(type(e)): {str(e)}}")
            return
        c_time = time.time()

        await message.edit(f"`Preparing to upload song:`\
        \n**{rip_data['title']}**\
        \nby *{rip_data['uploader']}*")
        await message.client.send_file(
            message.chat_id,
            f"{rip_data['id']}.mp3",
            supports_streaming=True,
            attributes=[
                DocumentAttributeAudio(duration=int(rip_data['duration']),
                                        title=str(rip_data['title']),
                                        performer=str(rip_data['uploader']))
            ],
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, message, c_time, "Uploading..",
                        f"{rip_data['title']}.mp3")))
        os.remove(f"{rip_data['id']}.mp3")
        await message.delete()