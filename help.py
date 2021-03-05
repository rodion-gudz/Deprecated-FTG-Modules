# -*- coding: utf-8 -*-

# Module author: Official Repo, @dekftgmodules, @ftgmodulesbyfl1yd

import logging
import inspect
import io
from .. import loader, utils, main, security

logger = logging.getLogger(__name__)


@loader.tds
class HelpMod(loader.Module):
    """Provides this help message"""
    strings = {"name": "Modules",
               "bad_module": "<b>Invalid module name specified</b>",
               "single_mod_header": ("<b>Help for</b> <u>{}</u>:\nNote that the monospace text are the commands "
                                     "and they can be run with <code>{}&lt;command&gt;</code>"),
               "single_cmd": "\n• <code><u>{}</u></code>\n",
               "undoc_cmd": "There is no documentation for this command",
               "all_header": "<b>Available Friendly-Telegram Modules:</b>",
               "mod_tmpl": "\n• <b>{}</b>",
               "first_cmd_tmpl": ": <code>{}",
               "cmd_tmpl": ", {}",
               "joined": "<b>Joined to</b> <a href='https://t.me/friendlytgbot'>support channel</a>",
               "join": "<b>Join the</b> <a href='https://t.me/friendlytgbot'>support channel</a>"}

    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.me = await client.get_me()
        self.db = db
        self.is_bot = await client.is_bot()

    @loader.unrestricted
    async def helpcmd(self, message):
        args = utils.get_args_raw(message)
        if args:
            module = None
            for mod in self.allmodules.modules:
                if mod.strings("name", message).lower() == args.lower():
                    module = mod
            if module is None:
                await utils.answer(message, self.strings("bad_module", message))
                return
            # Translate the format specification and the module separately
            try:
                name = module.strings("name", message)
            except KeyError:
                name = getattr(module, "name", "ERROR")
            reply = self.strings("single_mod_header", message).format(utils.escape_html(name),
                                                                      utils.escape_html((self.db.get(main.__name__,
                                                                                                     "command_prefix",
                                                                                                     False) or ".")[0]))
            if module.__doc__:
                reply += "\n" + "\n".join("  " + t for t in utils.escape_html(inspect.getdoc(module)).split("\n"))
            else:
                logger.warning("Module %s is missing docstring!", module)
            commands = {name: func for name, func in module.commands.items()
                        if await self.allmodules.check_security(message, func)}
            for name, fun in commands.items():
                reply += self.strings("single_cmd", message).format(name)
                if fun.__doc__:
                    reply += utils.escape_html("\n".join("  " + t for t in inspect.getdoc(fun).split("\n")))
                else:
                    reply += self.strings("undoc_cmd", message)
        else:
            reply = self.strings("all_header", message).format(utils.escape_html((self.db.get(main.__name__,
                                                                                              "command_prefix",
                                                                                              False) or ".")[0]))
            for mod in self.allmodules.modules:
                try:
                    name = mod.strings("name", message)
                except KeyError:
                    name = getattr(mod, "name", "ERROR")
                if name != "Logger" and name != "Raphielgang Configuration Placeholder" \
                        and name != "Uniborg configuration placeholder":
                    reply += self.strings("mod_tmpl", message).format(name)
                    first = True
                    commands = [name for name, func in mod.commands.items()
                                if await self.allmodules.check_security(message, func)]
                    for cmd in commands:
                        if first:
                            reply += self.strings("first_cmd_tmpl", message).format(cmd)
                            first = False
                        else:
                            reply += self.strings("cmd_tmpl", message).format(cmd)
                    reply += "</code>"
        await utils.answer(message, reply)

    async def restorecmd(self, m):
        """Установить все модули из txt файла"""
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
        await m.edit(f"[BackupMan]\n\nЗагружено: {valid}\nЗагружены ранее: {already_loaded}\n\n" + (
            "Необходима перезагрузка!\n<code>.restart</code>" if valid != 0 else "Ничего не загружено"))

    async def backupcmd(self, m):
        """
        Сделать бэкап модулей в txt файл
        """
        modules = self._db.get("friendly-telegram.modules.loader", "loaded_modules", [])
        txt = io.BytesIO("\n".join(modules).encode())
        txt.name = "BackupMan-{}.txt".format(str((await m.client.get_me()).id))
        await m.client.send_file(m.to_id, txt, caption=f"[BackupMan] Бэкап модулей\nМодулей: {len(modules)}")
        await m.delete()
        await m.client.send_file(m.to_id, txt, caption=f"[BackupMan] Бэкап модулей\nМодулей: {len(modules)}")
        await m.delete()

    async def modulecmd(self, message):
        """Вывести ссылку на модуль"""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit('Нет аргументов.')

        await message.edit('<b>Searching...</b>')

        try:
            f = ' '.join(
                [x.strings["name"] for x in self.allmodules.modules if args.lower() == x.strings["name"].lower()])
            r = inspect.getmodule(
                next(filter(lambda x: args.lower() == x.strings["name"].lower(), self.allmodules.modules)))

            link = str(r).split('(')[1].split(')')[0]
            if "http" not in link:
                text = f"File {f}:"
            else:
                text = f"<a href=\"{link}\">Link</a> for {f}: \n<code>{link}</code>"

            out = io.BytesIO(r.__loader__.data)
            out.name = f + ".py"
            out.seek(0)

            await message.respond(text, file=out)
            await message.delete()
        except:
            return await message.edit("Произошла непредвиденная ошибка")
