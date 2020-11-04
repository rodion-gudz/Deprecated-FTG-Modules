from .. import loader, utils

from telethon.errors.rpcerrorlist import MessageNotModifiedError

import logging
import asyncio
from asyncio import sleep
logger = logging.getLogger(__name__)


@loader.tds
class TyperMod(loader.Module):
    strings = {"name": "Text editor",
               "no_message": "<b>You can't type nothing!</b>",
               "type_char_cfg_doc": "Character for typewriter",
               "delay_typer_cfg_doc": "How long to delay showing the typewriter character",
               "delay_text_cfg_doc": "How long to delay showing the text"}

    def __init__(self):
        self.config = loader.ModuleConfig("TYPE_CHAR", "▒", lambda m: self.strings("type_char_cfg_doc", m),
                                          "DELAY_TYPER", 0.04, lambda m: self.strings("delay_typer_cfg_doc", m),
                                          "DELAY_TEXT", 0.02, lambda m: self.strings("delay_text_cfg_doc", m))

    @loader.ratelimit
    async def typecmd(self, message):
        """.type <message>"""
        a = utils.get_args_raw(message)
        if not a:
            await utils.answer(message, self.strings("no_message", message))
            return
        m = ""
        entities = message.entities or []
        for c in a:
            m += self.config["TYPE_CHAR"]
            message = await update_message(message, m, entities)
            await asyncio.sleep(0.04)
            m = m[:-1] + c
            message = await update_message(message, m, entities)
            await asyncio.sleep(0.02)

    async def printcmd(self, message):
        """.print <text or reply>"""
        text = utils.get_args_raw(message)
        if not text:
            reply = await message.get_reply_message()
            if not reply or not reply.message:
                await message.edit("<b>Текста нет!</b>")
                return
            text = reply.message
        out = ""
        for ch in text:
            out += ch
            if ch not in [" ", "\n"]:
                await message.edit(out + "\u2060")
                await sleep(0.3)

async def update_message(message, m, entities):
    try:
        return await utils.answer(message, m, parse_mode=lambda t: (t, entities))
    except MessageNotModifiedError:
        return message  # space doesnt count
