import logging

from .. import loader, utils

logger = logging.getLogger(__name__)
import os
import time
import os
from telethon import functions
from telethon import events
import asyncio
from telethon.tl.types import DocumentAttributeFilename
from telethon.errors.rpcerrorlist import YouBlockedUserError
from requests import get
from telethon import events


@loader.tds
class TranslateMod(loader.Module):
    """Translator"""
    strings = {"name": "Translator",
               "translated": "<b>From: </b><code>{from_lang}</code>"
                             "\n<b>To: </b><code>{to_lang}</code>\n\n{output}",
               "invalid_text": "Invalid text to translate",
               "doc_default_lang": "Language to translate to by default",
               "doc_api_key": "API key from https://translate.yandex.com/developers/keys"}

    @loader.unrestricted
    @loader.ratelimit
    async def translatecmd(self, event):
        chat = '@YTranslateBot'
        reply = await event.get_reply_message()
        async with event.client.conversation(chat) as conv:
            text = utils.get_args_raw(event)
            if reply:
                text = await event.get_reply_message()
            try:
                response = conv.wait_event(events.NewMessage(incoming=True, from_users=104784211))
                mm = await event.client.send_message(chat, text)
                response = await response
                await mm.delete()
            except YouBlockedUserError:
                await event.edit('<code>Разблокируй @ttsavebot</code>')
                return
            await event.edit(str(response.text).split(": ", 1)[1])
            await event.client(
                functions.messages.DeleteHistoryRequest(peer='YTranslateBot', max_id=0, just_clear=False, revoke=True))
