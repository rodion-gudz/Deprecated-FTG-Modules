# -*- coding: utf-8 -*-

# Module author: @ftgmodulesbyfl1yd

# requires: googletrans==4.0.0rc1

from .. import loader, utils
from googletrans import LANGUAGES, Translator
from telethon import functions
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon import events


@loader.tds
class TranslatorMod(loader.Module):
    """Translator Module"""
    strings = {'name': 'Translate'}

    async def gtrslcmd(self, message):
        """Используй: .gtrsl <с какого языка перевести> <на какой перевести>
        <текст> или .gtrsl <на какой перевести> <реплай>; langs. """
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        langs = LANGUAGES
        lang = args.split()
        tr = Translator().translate
        if not args and not reply:
            return await message.edit("Нет аргументов или реплая.")
        if args == "langs":
            return await message.edit(
                "<code>" + '\n'.join(str(langs).split(', ')) + "</code>")
        if reply:
            try:
                trslreply = True
                text = reply.text
                if len(lang) >= 2:
                    trslreply = False
                dest = langs[lang[0]]
                r = tr(args.split(' ', 1)[1] if trslreply is False else text,
                       dest=dest)
            except:
                r = tr(reply.text)
        else:
            try:
                try:
                    src = langs[lang[0]]
                    dest = langs[lang[1]]
                    text = args.split(' ', 2)[2]
                    r = tr(text, src=src, dest=dest)
                except:
                    dest = langs[lang[0]]
                    text = args.split(' ', 1)[1]
                    r = tr(text, dest=dest)
            except KeyError:
                r = tr(args)
        return await message.edit(f"<b>[{r.src} ➜ {r.dest}]</b>\n{r.text}")

    @loader.unrestricted
    @loader.ratelimit
    async def translatecmd(self, message):
        chat = '@YTranslateBot'
        reply = await message.get_reply_message()
        async with message.client.conversation(chat) as conv:
            text = utils.get_args_raw(message)
            if reply:
                text = await message.get_reply_message()
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=104784211))
                mm = await message.client.send_message(chat, text)
                response = await response
                await mm.delete()
            except YouBlockedUserError:
                await message.edit('<code>Разблокируй @YTranslateBot</code>')
                return
            await message.edit(str(response.text).split(": ", 1)[1])
            await message.client(
                functions.messages.DeleteHistoryRequest(peer='YTranslateBot',
                                                        max_id=0,
                                                        just_clear=False,
                                                        revoke=True))
