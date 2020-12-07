from random import choice, randint
from .. import loader, utils
from asyncio import sleep
from telethon import events, errors, functions, types

def register(cb):
    cb(FakeMod())

# options = ['typing', 'contact', 'game', 'location', 'record-audio', 'record-round',
#                    'record-video', 'voice', 'round', 'video', 'photo', 'document', 'cancel']

class FakeMod(loader.Module):

    strings = {'name': 'Fake Actions'}

    async def typecmd(self, event):
        scam_time = randint(30, 60)
        try:
            await event.delete()
            async with event.client.action(event.chat_id, 'typing'):
                await sleep(scam_time)
        except BaseException:
            return
    async def voicecmd(self, event):
        scam_time = randint(30, 60)
        try:
            await event.delete()
            async with event.client.action(event.chat_id, 'record-audio'):
                await sleep(scam_time)
        except BaseException:
            return
    async def gamecmd(self, event):
        scam_time = randint(30, 60)
        try:
            await event.delete()
            async with event.client.action(event.chat_id, 'game'):
                await sleep(scam_time)
        except BaseException:
            return
    async def videocmd(self, event):
        scam_time = randint(30, 60)
        try:
            await event.delete()
            async with event.client.action(event.chat_id, 'record-video'):
                await sleep(scam_time)
        except BaseException:
            return
    async def photocmd(self, event):
        scam_time = randint(30, 60)
        try:
            await event.delete()
            async with event.client.action(event.chat_id, 'photo'):
                await sleep(scam_time)
        except BaseException:
            return
    async def documentcmd(self, event):
        scam_time = randint(30, 60)
        try:
            await event.delete()
            async with event.client.action(event.chat_id, 'document'):
                await sleep(scam_time)
        except BaseException:
            return
    async def locationcmd(self, event):
        scam_time = randint(30, 60)
        try:
            await event.delete()
            async with event.client.action(event.chat_id, 'document'):
                await sleep(scam_time)
        except BaseException:
            return
    async def cancelcmd(self, event):
        scam_time = randint(30, 60)
        try:
            await event.delete()
            async with event.client.action(event.chat_id, 'cancel'):
                await sleep(scam_time)
        except BaseException:
            return

    async def scrncmd(self, message):
        a = 1
        r = utils.get_args(message)
        if r and r[0].isdigit():
            a = int(r[0])
        await message.edit("Screenshoting...")
        for _ in range(a):
            await message.client(
                functions.messages.SendScreenshotNotificationRequest(peer=message.to_id, reply_to_msg_id=message.id))
        await message.delete()