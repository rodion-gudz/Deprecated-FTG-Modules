# -*- coding: utf-8 -*-

# Module author: @hftgmodulesbyfl1yd, @GovnoCodules

from random import choice, randint
from .. import loader, utils
from asyncio import sleep
from telethon import events, errors, functions, types


def register(cb):
    cb(FakeMod())


class FakeMod(loader.Module):
    """Imitates your actions"""
    strings = {'name': 'Fake Actions'}

    async def typecmd(self, event):
        """Imitates typing"""
        activity_time = utils.get_args(event)
        if activity_time:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'typing'):
                    await sleep(int(activity_time[0]))
            except BaseException:
                return
        else:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'typing'):
                    await sleep(randint(30, 60))
            except BaseException:
                return

    async def voicecmd(self, event):
        """Imitates sending voices"""
        activity_time = utils.get_args(event)
        if activity_time:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'voice'):
                    await sleep(int(activity_time[0]))
            except BaseException:
                return
        else:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'voice'):
                    await sleep(randint(30, 60))
            except BaseException:
                return

    async def gamecmd(self, event):
        """Imitates your game activity"""
        activity_time = utils.get_args(event)
        if activity_time:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'game'):
                    await sleep(int(activity_time[0]))
            except BaseException:
                return
        else:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'game'):
                    await sleep(randint(30, 60))
            except BaseException:
                return

    async def videocmd(self, event):
        """Imitates sending video"""
        activity_time = utils.get_args(event)
        if activity_time:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'video'):
                    await sleep(int(activity_time[0]))
            except BaseException:
                return
        else:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'video'):
                    await sleep(randint(30, 60))
            except BaseException:
                return

    async def photocmd(self, event):
        """Imitates sending photo"""
        activity_time = utils.get_args(event)
        if activity_time:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'photo'):
                    await sleep(int(activity_time[0]))
            except BaseException:
                return
        else:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'photo'):
                    await sleep(randint(30, 60))
            except BaseException:
                return

    async def documentcmd(self, event):
        """Imitates sending document"""
        activity_time = utils.get_args(event)
        if activity_time:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'document'):
                    await sleep(int(activity_time[0]))
            except BaseException:
                return
        else:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'document'):
                    await sleep(randint(30, 60))
            except BaseException:
                return

    async def locationcmd(self, event):
        """Imitates sending location"""
        activity_time = utils.get_args(event)
        if activity_time:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'location'):
                    await sleep(int(activity_time[0]))
            except BaseException:
                return
        else:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'location'):
                    await sleep(randint(30, 60))
            except BaseException:
                return

    async def contactcmd(self, event):
        """Imitates sending contact"""
        activity_time = utils.get_args(event)
        if activity_time:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'contact'):
                    await sleep(int(activity_time[0]))
            except BaseException:
                return
        else:
            try:
                await event.delete()
                async with event.client.action(event.chat_id, 'contact'):
                    await sleep(randint(30, 60))
            except BaseException:
                return

    async def scrncmd(self, message):
        """Screenshot notification (Only PM)"""
        a = 1
        r = utils.get_args(message)
        if r and r[0].isdigit():
            a = int(r[0])
        for _ in range(a):
            await message.client(
                functions.messages.SendScreenshotNotificationRequest(peer=message.to_id, reply_to_msg_id=message.id))
        await message.delete()
