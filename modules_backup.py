from telethon import functions, types, events
from .. import loader, utils
import re
import io


def register(cb):
    cb(BackupManMod())


class BackupManMod(loader.Module):
    """BackupMan"""
    strings = {'name': 'Modules backup'}

    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.me = await client.get_me()

    async def restorecmd(self, m):
        """
        Установить все модули из txt файла
        """
        reply = await m.get_reply_message()
        if not reply:
            await m.edit("REPLY_TO_TXT")
            return
        if not reply.file:
            await m.edit("REPLY_TO_TXT")
            return
        if reply.file.ext != ".txt":
            await m.edit("REPLY_TO_TXT")
            return
        modules = self._db.get("friendly-telegram.modules.loader", "loaded_modules", [])
        txt = io.BytesIO()
        await reply.download_media(txt)
        txt.seek(0)
        valid = 0
        already_loaded = 0
        inclink = 0
        for i in txt.read().decode('utf-8').split("\n"):
            if i not in modules:
                valid += 1
                modules.append(i)
            else:
                already_loaded += 1
        self._db.set("friendly-telegram.modules.loader", "loaded_modules", modules)
        await m.edit(f"Restored: {valid}\n" + (
            "Please restart!\n<code>.restart</code>" if valid != 0 else "Nothing loaded"))

    async def backupcmd(self, m):
        """
        Сделать бэкап модулей в txt файл
        """
        modules = self._db.get("friendly-telegram.modules.loader", "loaded_modules", [])
        txt = io.BytesIO("\n".join(modules).encode())
        txt.name = "Modules Backup-{}.txt".format(str((await m.client.get_me()).id))
        await m.client.send_file(m.to_id, txt, caption=f"Modules backup completed\nSaved modlues: {len(modules)}")
        await m.delete()
        await m.client.send_file(m.to_id, txt, caption=f"Modules backup completed\nSaved modules: {len(modules)}")
        await m.delete()



