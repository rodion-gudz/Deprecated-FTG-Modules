# -*- coding: utf-8 -*-

# Module author: @GovnoCodules

import traceback
import sys
import itertools
import types
from meval import meval
import logging
import asyncio
import re
import telethon

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ExecutorMod(loader.Module):
    """Stores global notes (aka snips)"""
    strings = {"name": "Notexec",
               "what_note": "<b>What notexec should be executed?</b>",
               "no_note": "<b>Notexec not found</b>",
               "execute_fail": "<b>Failed to execute expression:</b>\n<code>{}</code>",
               "flood_wait_protect_cfg_doc": "How long to wait in seconds between edits in commands",
               "what_to_kill": "<b>Reply to a terminal command to terminate it</b>",
               "kill_fail": "<b>Could not kill process</b>",
               "killed": "<b>Killed</b>",
               "no_cmd": "<b>No command is running in that message</b>",
               "running": "<b>Running command</b> <code>{}</code>",
               "finished": "\n<b>Command finished with return code</b> <code>{}</code>",
               "stdout": "\n<b>Stdout:</b>\n<code>",
               "stderr": "</code>\n\n<b>Stderr:</b>\n<code>",
               "end": "</code>",
               "auth_fail": "<b>Authentication failed, please try again</b>",
               "auth_needed": "<a href=\"tg://user?id={}\">Interactive authentication required</a>",
               "auth_msg": ("<b>Please edit this message to the password for</b> "
                            "<code>{}</code> <b>to run</b> <code>{}</code>"),
               "auth_locked": "<b>Authentication failed, please try again later</b>",
               "auth_ongoing": "<b>Authenticating...</b>",
               "done": "<b>Done</b>"
               }

    def __init__(self):
        self.config = loader.ModuleConfig("FLOOD_WAIT_PROTECT", 2,
                                          lambda m: self.strings("flood_wait_protect_cfg_doc"))
        self.activecmds = {}

    async def notexeccmd(self, message):
        """Gets the note specified"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("what_note", message))
            return

        asset_id = self._db.get("friendly-telegram.modules.notes", "notes", {}).get(args[0], None)
        logger.debug(asset_id)
        if asset_id is not None:
            asset = await self._db.fetch_asset(asset_id)
        else:
            asset_id = self._db.get("friendly-telegram.modules.notes", "notes", {}).get(args[0].lower(), None)
            if asset_id is not None:
                asset = await self._db.fetch_asset(asset_id)
            else:
                asset = None
        if asset is None:
            await utils.answer(message, self.strings("no_note", message))
            return

        cmd = await self._db.fetch_asset(asset_id)

        try:
            await meval(cmd.raw_text, globals(), **await self.getattrs(message))
        except Exception:
            exc = sys.exc_info()
            exc = "".join(traceback.format_exception(exc[0], exc[1], exc[2].tb_next.tb_next.tb_next))
            await utils.answer(message, self.strings("execute_fail", message)
                               .format(utils.escape_html(exc)))
            return

    async def noterminalcmd(self, message):
        """Gets the note specified"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("what_note", message))
            return

        asset_id = self.db.get("friendly-telegram.modules.notes", "notes", {}).get(args[0], None)
        logger.debug(asset_id)
        if asset_id is not None:
            asset = await self.db.fetch_asset(asset_id)
        else:
            asset_id = self.db.get("friendly-telegram.modules.notes", "notes", {}).get(args[0].lower(), None)
            if asset_id is not None:
                asset = await self.db.fetch_asset(asset_id)
            else:
                asset = None
        if asset is None:
            await utils.answer(message, self.strings("no_note", message))
            return

        cmd = await self.db.fetch_asset(asset_id)
        await self.run_command(message, cmd.raw_text)

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._db = db

    async def getattrs(self, message):
        return {"message": message, "client": self.client, "self": self, "db": self.db,
                "reply": await message.get_reply_message(), "chat": message.to_id,
                **self.get_types(),
                **self.get_functions()}

    def get_types(self):
        return self.get_sub(telethon.tl.types)

    def get_functions(self):
        return self.get_sub(telethon.tl.functions)

    def get_sub(self, it, _depth=1):
        """Get all callable capitalised objects in an object recursively, ignoring _*"""
        return {**dict(filter(lambda x: x[0][0] != "_" and x[0][0].upper() == x[0][0] and callable(x[1]),
                              it.__dict__.items())),
                **dict(itertools.chain.from_iterable([self.get_sub(y[1], _depth + 1).items() for y in
                                                      filter(lambda x: x[0][0] != "_"
                                                                       and isinstance(x[1], types.ModuleType)
                                                                       and x[1] != it
                                                                       and x[1].__package__.rsplit(".", _depth)[0]
                                                                       == "telethon.tl",
                                                             it.__dict__.items())]))}

    async def run_command(self, message, cmd, editor=None):
        if len(cmd.split(" ")) > 1 and cmd.split(" ")[0] == "sudo":
            needsswitch = True
            for word in cmd.split(" ", 1)[1].split(" "):
                if word[0] != "-":
                    break
                if word == "-S":
                    needsswitch = False
            if needsswitch:
                cmd = " ".join([cmd.split(" ", 1)[0], "-S", cmd.split(" ", 1)[1]])
        sproc = await asyncio.create_subprocess_shell(cmd, stdin=asyncio.subprocess.PIPE,
                                                      stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                                                      cwd=utils.get_base_dir())
        if editor is None:
            editor = SudoMessageEditor(message, cmd, self.config, self.strings, message)
        editor.update_process(sproc)
        self.activecmds[hash_msg(message)] = sproc
        await editor.redraw()
        await asyncio.gather(read_stream(editor.update_stdout, sproc.stdout, self.config["FLOOD_WAIT_PROTECT"]),
                             read_stream(editor.update_stderr, sproc.stderr, self.config["FLOOD_WAIT_PROTECT"]))
        await editor.cmd_ended(await sproc.wait())
        del self.activecmds[hash_msg(message)]

    @loader.owner
    async def noterminatecmd(self, message):
        """Use in reply to send SIGTERM to a process"""
        if not message.is_reply:
            await utils.answer(message, self.strings("what_to_kill", message))
            return
        if hash_msg(await message.get_reply_message()) in self.activecmds:
            try:
                self.activecmds[hash_msg(await message.get_reply_message())].terminate()
            except Exception:
                logger.exception("Killing process failed")
                await utils.answer(message, self.strings("kill_fail", message))
            else:
                await utils.answer(message, self.strings("killed", message))
        else:
            await utils.answer(message, self.strings("no_cmd", message))

    @loader.owner
    async def nokillcmd(self, message):
        """Use in reply to send SIGKILL to a process"""
        if not message.is_reply:
            await utils.answer(message, self.strings("what_to_kill", message))
            return
        if hash_msg(await message.get_reply_message()) in self.activecmds:
            try:
                self.activecmds[hash_msg(await message.get_reply_message())].kill()
            except Exception:
                logger.exception("Killing process failed")
                await utils.answer(message, self.strings("kill_fail", message))
            else:
                await utils.answer(message, self.strings("killed", message))
        else:
            await utils.answer(message, self.strings("no_cmd", message))


def hash_msg(message):
    return str(utils.get_chat_id(message)) + "/" + str(message.id)


async def read_stream(func, stream, delay):
    last_task = None
    data = b""
    while True:
        dat = (await stream.read(1))
        if not dat:
            # EOF
            if last_task:
                # Send all pending data
                last_task.cancel()
                await func(data.decode("utf-8"))
                # If there is no last task there is inherently no data, so theres no point sending a blank string
            break
        data += dat
        if last_task:
            last_task.cancel()
        last_task = asyncio.ensure_future(sleep_for_task(func, data, delay))


async def sleep_for_task(func, data, delay):
    await asyncio.sleep(delay)
    await func(data.decode("utf-8"))


class MessageEditor:
    def __init__(self, message, command, config, strings, request_message):
        self.message = [message]
        self.command = command
        self.stdout = ""
        self.stderr = ""
        self.rc = None
        self.redraws = 0
        self.config = config
        self.strings = strings
        self.request_message = request_message

    async def update_stdout(self, stdout):
        self.stdout = stdout
        await self.redraw()

    async def update_stderr(self, stderr):
        self.stderr = stderr
        await self.redraw()

    async def redraw(self):
        text = ""  # self.strings("running", self.request_message).format(utils.escape_html(self.command))
        # if self.rc is not None:
        #  text += self.strings("finished", self.request_message).format(utils.escape_html(str(self.rc)))
        text += self.strings("stdout")
        text += utils.escape_html(self.stdout[max(len(self.stdout) - 2048, 0):])
        if len(self.stderr) > 0:
            text += self.strings("stderr")
            text += utils.escape_html(self.stderr[max(len(self.stderr) - 1024, 0):])
        text += self.strings("end")
        try:
            self.message = await utils.answer(self.message, text)
        except telethon.errors.rpcerrorlist.MessageNotModifiedError:
            pass
        except telethon.errors.rpcerrorlist.MessageTooLongError as e:
            logger.error(e)
            logger.error(text)
        # The message is never empty due to the template header

    async def cmd_ended(self, rc):
        self.rc = rc
        self.state = 4
        await self.redraw()

    def update_process(self, process):
        pass


class SudoMessageEditor(MessageEditor):
    # Let's just hope these are safe to parse
    PASS_REQ = "[sudo] password for"
    WRONG_PASS = r"\[sudo\] password for (.*): Sorry, try again\."
    TOO_MANY_TRIES = r"\[sudo\] password for (.*): sudo: [0-9]+ incorrect password attempts"

    def __init__(self, message, command, config, strings, request_message):
        super().__init__(message, command, config, strings, request_message)
        self.process = None
        self.state = 0
        self.authmsg = None

    def update_process(self, process):
        logger.debug("got sproc obj %s", process)
        self.process = process

    async def update_stderr(self, stderr):
        logger.debug("stderr update " + stderr)
        self.stderr = stderr
        lines = stderr.strip().split("\n")
        lastline = lines[-1]
        lastlines = lastline.rsplit(" ", 1)
        handled = False
        if len(lines) > 1 and re.fullmatch(self.WRONG_PASS,
                                           lines[-2]) and lastlines[0] == self.PASS_REQ and self.state == 1:
            logger.debug("switching state to 0")
            await self.authmsg.edit(self.strings("auth_failed"))
            self.state = 0
            handled = True
            await asyncio.sleep(2)
            await self.authmsg.delete()
        if lastlines[0] == self.PASS_REQ and self.state == 0:
            logger.debug("Success to find sudo log!")
            text = self.strings("auth_needed").format((await self.message[0].client.get_me()).id)
            try:
                await utils.answer(self.message, text)
            except telethon.errors.rpcerrorlist.MessageNotModifiedError as e:
                logger.debug(e)
            logger.debug("edited message with link to self")
            command = "<code>" + utils.escape_html(self.command) + "</code>"
            user = utils.escape_html(lastlines[1][:-1])
            self.authmsg = await self.message[0].client.send_message("me",
                                                                     self.strings("auth_msg").format(command, user))
            logger.debug("sent message to self")
            self.message[0].client.remove_event_handler(self.on_message_edited)
            self.message[0].client.add_event_handler(self.on_message_edited,
                                                     telethon.events.messageedited.MessageEdited(chats=["me"]))
            logger.debug("registered handler")
            handled = True
        if len(lines) > 1 and (re.fullmatch(self.TOO_MANY_TRIES, lastline)
                               and (self.state == 1 or self.state == 3 or self.state == 4)):
            logger.debug("password wrong lots of times")
            await utils.answer(self.message, self.strings("auth_locked"))
            await self.authmsg.delete()
            self.state = 2
            handled = True
        if not handled:
            logger.debug("Didn't find sudo log.")
            if self.authmsg is not None:
                await self.authmsg[0].delete()
                self.authmsg = None
            self.state = 2
            await self.redraw()
        logger.debug(self.state)

    async def update_stdout(self, stdout):
        self.stdout = stdout
        if self.state != 2:
            self.state = 3  # Means that we got stdout only
        if self.authmsg is not None:
            await self.authmsg.delete()
            self.authmsg = None
        await self.redraw()

    async def on_message_edited(self, message):
        # Message contains sensitive information.
        if self.authmsg is None:
            return
        logger.debug("got message edit update in self " + str(message.id))
        if hash_msg(message) == hash_msg(self.authmsg):
            # The user has provided interactive authentication. Send password to stdin for sudo.
            try:
                self.authmsg = await utils.answer(message, self.strings("auth_ongoing"))
            except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                await message.delete()
            self.state = 1
            self.process.stdin.write(message.message.message.split("\n", 1)[0].encode("utf-8") + b"\n")


class RawMessageEditor(SudoMessageEditor):
    def __init__(self, message, command, config, strings, request_message, show_done=False):
        super().__init__(message, command, config, strings, request_message)
        self.show_done = show_done

    async def redraw(self):
        logger.debug(self.rc)
        if self.rc is None:
            text = "<code>" + utils.escape_html(self.stdout[max(len(self.stdout) - 4095, 0):]) + "</code>"
        elif self.rc == 0:
            text = "<code>" + utils.escape_html(self.stdout[max(len(self.stdout) - 4090, 0):]) + "</code>"
        else:
            text = "<code>" + utils.escape_html(self.stderr[max(len(self.stderr) - 4095, 0):]) + "</code>"
        if self.rc is not None and self.show_done:
            text += "\n" + self.strings("done")
        logger.debug(text)
        try:
            await utils.answer(self.message, text)
        except telethon.errors.rpcerrorlist.MessageNotModifiedError:
            pass
        except (telethon.errors.rpcerrorlist.MessageEmptyError, ValueError):
            pass
        except telethon.errors.rpcerrorlist.MessageTooLongError as e:
            logger.error(e)
            logger.error(text)
