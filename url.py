
import logging
from .. import loader, utils
import telethon
from requests import post
import urllib
logger = logging.getLogger(__name__)
import os
import re
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
from requests import get, post, exceptions
import asyncio
import os
from telethon import functions, types
from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, LOGS, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register



@loader.tds
class GGdotGGMod(loader.Module):
    strings = {
        "name": "URL utils",
        "some_rong": "<b>Ты делаешь что-то не так!\nНапиши</b> <code>.help gg.gg</code> <b>для информации.</b>",
        "result": "<a href='{}'>{}</a>",
        "default": "How to use Google?"
    }

    async def client_ready(self, client, db):
        self.client = client

    async def ggcmd(self, message):
        m_text = utils.get_args_raw(message)
        if not m_text:
            reply = await message.get_reply_message()
            if not reply:
                await utils.answer(message, self.strings["some_rong"])
                return
            long_url = reply.raw_text
        else:
            long_url = m_text

        if 'http://' not in long_url and 'https://' not in long_url:
            long_url = 'http://' + long_url
        await utils.answer(message, "Creating...")
        short = post('http://gg.gg/create',
                     data={'custom_path': None, 'use_norefs': '0', 'long_url': long_url, 'app': 'site',
                           'version': '0.1'}).text
        await utils.answer(message, short)
    async def nullcmd(self, event):
        chat = '@nullifybot'
        reply = await event.get_reply_message()
        async with event.client.conversation(chat) as conv:
            if not reply:
                text = utils.get_args_raw(event)
            else:
                text = await event.get_reply_message()
            try:
                response = conv.wait_event(events.NewMessage(incoming=True, from_users=1481485420))
                mm = await event.client.send_message(chat, text)
                response = await response
                await mm.delete()
            except YouBlockedUserError:
                await event.edit('<code>Разблокируй @nullifybot</code>')
                return
            await event.edit(response.text.replace("🔗 Твоя ссылка: ", ""))
            await event.client(functions.messages.DeleteHistoryRequest(
                peer='nullifybot',
                max_id=0,
                just_clear=False,
                revoke=True
            ))

    async def lgtcmd(self, message):
        args = utils.get_args_raw(message)
        if not args: return await message.edit("Нет аргументов.")
        link = os.popen(f"curl verylegit.link/sketchify -d long_url={args}").read()
        await message.edit(f"{link}")

    async def clckcmd(self, message):
        m_text = utils.get_args_raw(message)
        if not m_text:
            reply = await message.get_reply_message()
            if not reply:
                await utils.answer(message, self.strings["some_rong"])
                return
            long_url = reply.raw_text
        else:
            long_url = m_text
        await utils.answer(message, "Creating...")
        fetcher = post(
            'https://clck.ru/--?url=' +
            long_url).text
        await utils.answer(message, fetcher)

    async def lmgtfycmd(self, message):
        """Use in reply to another message or as .lmgtfy <text>"""
        text = utils.get_args_raw(message)
        if not text:
            if message.is_reply:
                text = (await message.get_reply_message()).message
            else:
                text = self.strings("default", message)
        query_encoded = urllib.parse.quote_plus(text)
        lmgtfy_url = "http://lmgtfy.com/?s=g&iie=1&q={}".format(query_encoded)
        await utils.answer(message,
                           self.strings("result", message).format(utils.escape_html(lmgtfy_url),
                                                                  utils.escape_html(text)))

