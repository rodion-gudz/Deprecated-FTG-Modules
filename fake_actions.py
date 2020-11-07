from random import choice, randint
from .. import loader, utils
from asyncio import sleep


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