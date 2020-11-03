import logging
from .. import loader, utils
import telethon

logger = logging.getLogger(__name__)


async def register(cb):
    cb(KeyboardSwitcherMod())


@loader.tds
class KeyboardSwitcherMod(loader.Module):
    strings = {
        "name": "Keyboard switcher"}

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

