
import logging
from .. import loader, utils
import telethon
from requests import post
import urllib
logger = logging.getLogger(__name__)
import os




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

