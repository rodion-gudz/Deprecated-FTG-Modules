from .. import loader, utils

from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon.tl.types import DocumentAttributeFilename
from telethon.errors.rpcerrorlist import YouBlockedUserError
import logging
import asyncio
from asyncio import sleep
logger = logging.getLogger(__name__)
import io
from .. import loader, utils
import io
from base64 import b64encode, b64decode
import logging
from .. import loader, utils
import telethon

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
    async def typercmd(self, message):
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

    async def b64encodecmd(self, message):
        reply = await message.get_reply_message()
        mtext = utils.get_args_raw(message)
        if message.media:
            await message.edit("<b>Загрузка файла...</b>")
            data = await message.client.download_file(mtext, bytes)
        elif mtext:
            data = bytes(mtext, "utf-8")
        elif reply:
            if reply.media:
                await message.edit("<b>Загрузка файла...</b>")
                data = await message.client.download_file(reply, bytes)
            else:
                data = bytes(reply.raw_text, "utf-8")
        else:
            await message.edit(f"<b>Что нужно закодировать?</b>")
        output = b64encode(data)
        if len(output) > 4000:
            output = io.BytesIO(output)
            output.name = "base64.txt"
            output.seek(0)
            await message.client.send_file(message.to_id, output, reply_to=reply)
            await message.delete()
        else:
            await message.edit(str(output, "utf-8"))

    @loader.owner
    async def b64decodecmd(self, message):
        reply = await message.get_reply_message()
        mtext = utils.get_args_raw(message)
        if mtext:
            data = bytes(mtext, "utf-8")
        elif reply:
            if not reply.message:
                await message.edit("<b>Расшифровка файлов невозможна...</b>")
                return
            else:
                data = bytes(reply.raw_text, "utf-8")
        else:
            await message.edit(f"<b>Что нужно декодировать?</b>")
            return
        try:
            output = b64decode(data)
            await message.edit(str(output, "utf-8"))
        except:
            await message.edit("<b>Ошибка декодирования!</b>")
            return

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

    async def codecmd(self, message):
        if message.is_reply:
            reply = await message.get_reply_message()
            code = reply.raw_text
            code = code.replace("<", "&lt;").replace(">", "&gt;")
            await message.edit(f"<code>{code}</code>")
        else:
            code = message.raw_text[5:]
            code = code.replace("<", "&lt;").replace(">", "&gt;")
            try:
                await message.edit(f"<code>{code}</code>")
            except:
                await message.edit(self.strings["msg_is_emp"])

        async def switchcmd(self, message):
            """Если ты допустил ошибку и набрал текст не сменив раскладку клавиатуры
    то вернись в его начало и допиши `.switch` и твой текст станет читабельным.
    Если ты всё же отправил сообщение не в той расскладке, то просто ответь на него этой командой и он измениться.
    если же твой собеседник допустил ошибку, то просто ответь на его сообщение и сообщение с командой измениться."""
            RuKeys = """ёйцукенгшщзхъфывапролджэячсмитьбю.Ё"№;%:?ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"""
            EnKeys = """`qwertyuiop[]asdfghjkl;'zxcvbnm,./~@#$%^&QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?"""

            if message.is_reply:
                reply = await message.get_reply_message()
                text = reply.raw_text
                if not text:
                    await message.edit('Тут текста нету...')
                    return
                change = str.maketrans(RuKeys + EnKeys, EnKeys + RuKeys)
                text = str.translate(text, change)

                if message.from_id != reply.from_id:
                    await message.edit(text)
                else:
                    await message.delete()
                    await reply.edit(text)

            else:
                text = utils.get_args_raw(message)
                if not text:
                    await message.edit('Тут текста нету...')
                    return
                change = str.maketrans(RuKeys + EnKeys, EnKeys + RuKeys)
                text = str.translate(text, change)
                await message.edit(text)

    async def deltypecmd(self, message):
        """.quicktype <timeout> <message>"""
        args = utils.get_args(message)
        logger.debug(args)
        if len(args) == 0:
            await utils.answer(message, self.strings("need_something", message))
            return
        if len(args) == 1:
            await utils.answer(message, self.strings("lazy_af", message))
            return
        t = args[0]
        mess = " ".join(args[1:])
        try:
            t = float(t)
        except ValueError:
            await utils.answer(message, self.strings("nice_number", message))
            return
        await utils.answer(message, mess)
        await asyncio.sleep(t)
        await message.delete()

    async def mtfcmd(self, message):
        reply = await message.get_reply_message()
        if not reply or not reply.message:
            await message.edit("<b>Reply to text!</b>")
            return
        text = bytes(reply.raw_text, "utf8")
        fname = utils.get_args_raw(message) or str(message.id + reply.id) + ".txt"
        file = io.BytesIO(text)
        file.name = fname
        file.seek(0)
        await reply.reply(file=file)
        await message.delete()

    async def ftmcmd(self, message):
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await message.edit("<b>Reply to file!</b>")
            return
        text = await reply.download_media(bytes)
        text = str(text, "utf8")
        if utils.get_args(message):
            text = f"<code>{text}</code>"
        await utils.answer(message, utils.escape_html(text))

    async def switchcmd(self, message):
        RuKeys = """ёйцукенгшщзхъфывапролджэячсмитьбю.Ё"№;%:?ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"""
        EnKeys = """`qwertyuiop[]asdfghjkl;'zxcvbnm,./~@#$%^&QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?"""

        if message.is_reply:
            reply = await message.get_reply_message()
            text = reply.raw_text
            if not text:
                await message.edit('Тут текста нету...')
                return
            change = str.maketrans(RuKeys + EnKeys, EnKeys + RuKeys)
            text = str.translate(text, change)

            if message.from_id != reply.from_id:
                await message.edit(text)
            else:
                await message.delete()
                await reply.edit(text)

        else:
            text = utils.get_args_raw(message)
            if not text:
                await message.edit('Тут текста нету...')
                return
            change = str.maketrans(RuKeys + EnKeys, EnKeys + RuKeys)
            text = str.translate(text, change)
            await message.edit(text)

async def update_message(message, m, entities):
    try:
        return await utils.answer(message, m, parse_mode=lambda t: (t, entities))
    except MessageNotModifiedError:
        return message  # space doesnt count
