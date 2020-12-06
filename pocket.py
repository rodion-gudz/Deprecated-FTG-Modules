from telethon import functions
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from .. import loader, utils

def register(cb):
    cb(ReplyDownloaderMod())


class ReplyDownloaderMod(loader.Module):
    strings = {'name': 'Pocket'}

    async def savepcmd(self, event):
        chat = '@pockebot'
        reply = await event.get_reply_message()
        async with event.client.conversation(chat) as conv:
            text = utils.get_args_raw(event)
            if reply:
                text = str(await event.get_reply_message())
                if len(utils.get_args_raw(event)) != 0:
                    text += utils.get_args_raw(event)
            await event.delete()
            await event.client(functions.messages.DeleteHistoryRequest(
                peer='pockebot',
                max_id=0,
                just_clear=False,
                revoke=True
            ))



