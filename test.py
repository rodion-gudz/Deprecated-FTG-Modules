# -*- coding: utf-8 -*-

# Module author: Official Repo

# requires: speedtest-cli>=2.1.0

from .. import loader, utils
from datetime import datetime
import logging
import time
from io import BytesIO
import speedtest

logger = logging.getLogger(__name__)


@loader.test(args=None)
async def dumptest(conv):
    m = await conv.send_message("test")
    await conv.send_message(".dump", reply_to=m)
    r = await conv.get_response()
    assert r.message.startswith("Message(") and "test" in r.message, r


@loader.test(args=("0", "FORCE_INSECURE"))
async def logstest(conv):
    r = await conv.get_response()
    assert r.message == "Loading media...", r
    r2 = await conv.get_response()
    assert r2.document, r2


@loader.tds
class TestMod(loader.Module):
    """Self-tests"""
    strings = {"name": "Tester",
               "pong": "Pong",
               "bad_loglevel": ("<b>Invalid loglevel. Please refer to </b>"
                                "<a href='https://docs.python.org/3/library/logging.html#logging-levels'>"
                                "the docs</a><b>.</b>"),
               "set_loglevel": "<b>Please specify verbosity as an integer or string</b>",
               "uploading_logs": "<b>Uploading logs...</b>",
               "no_logs": "<b>You don't have any logs at verbosity {}.</b>",
               "logs_filename": "ftg-logs.txt",
               "logs_caption": "friendly-telegram logs with verbosity {}",
               "logs_unsafe": ("<b>Warning: running this command may reveal personal or dangerous information. "
                               "You can write</b> <code>{}</code> <b>at the end to accept the risks</b>"),
               "logs_force": "FORCE_INSECURE",
               "suspend_invalid_time": "<b>Invalid time to suspend</b>",
               "running": "<b>Running speedtest...</b>",
               "results": "<b>Speedtest Results:</b>",
               "results_download": "<b>Download:</b> <code>{}</code> <b>MiB/s</b>",
               "results_upload": "<b>Upload:</b> <code>{}</code> <b>MiB/s</b>",
               "results_ping": "<b>Ping:</b> <code>{}</code> <b>ms</b>"}

    @loader.test(resp="Pong")
    @loader.unrestricted
    async def pingcmd(self, message):
        """Test your userbot ping"""
        start = datetime.now()
        await utils.answer(message, "<code>Ping checking...</code>")
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        await utils.answer(message, "<b>Ping:</b> <code>{}ms</code>".format(ms))

    @loader.test(func=dumptest)
    async def dumpcmd(self, message):
        """Use in reply to get a dump of a message"""
        if not message.is_reply:
            return
        await utils.answer(message, "<code>"
                           + utils.escape_html((await message.get_reply_message()).stringify()) + "</code>")

    @loader.test(func=logstest)
    async def logscmd(self, message):
        """.logs <level>
           Dumps logs. Loglevels below WARNING may contain personal info."""
        args = utils.get_args(message)
        if not len(args) == 1 and not len(args) == 2:
            await utils.answer(message, self.strings("set_loglevel", message))
            return
        try:
            lvl = int(args[0])
        except ValueError:
            # It's not an int. Maybe it's a loglevel
            lvl = getattr(logging, args[0].upper(), None)
        if not isinstance(lvl, int):
            await utils.answer(message, self.strings("bad_loglevel", message))
            return
        if not (lvl >= logging.WARNING or (len(args) == 2 and args[1] == self.strings("logs_force"))):
            await utils.answer(message,
                               self.strings("logs_unsafe", message).format(utils.escape_html(self.strings("logs_force", message))))
            return
        [handler] = logging.getLogger().handlers
        logs = ("\n".join(handler.dumps(lvl))).encode("utf-16")
        if not len(logs) > 0:
            await utils.answer(message, self.strings("no_logs", message).format(lvl))
            return
        logs = BytesIO(logs)
        logs.name = self.strings("logs_filename", message)
        await utils.answer(message, logs, caption=self.strings("logs_caption", message).format(lvl))

    @loader.owner
    async def suspendcmd(self, message):
        """.suspend <time>
           Suspends the bot for N seconds"""
        # Blocks asyncio message loop, preventing ANYTHING happening (except multithread ops,
        # but they will be blocked on return).
        try:
            time.sleep(int(utils.get_args_raw(message)))
        except ValueError:
            await utils.answer(message, self.strings("suspend_invalid_time", message))

    async def speedtestcmd(self, message):
        """Tests your internet speed"""
        await utils.answer(message, self.strings("running", message))
        args = utils.get_args(message)
        servers = []
        for server in args:
            try:
                servers += [int(server)]
            except ValueError:
                logger.warning("server failed")
        results = await utils.run_sync(self.speedtest, servers)
        ret = self.strings("results") + "\n\n"
        ret += self.strings("results_download", message).format(round(results["download"] / 2 ** 20, 2)) + "\n"
        ret += self.strings("results_upload", message).format(round(results["upload"] / 2 ** 20, 2)) + "\n"
        ret += self.strings("results_ping", message).format(round(results["ping"], 2)) + "\n"
        await utils.answer(message, ret)

    def speedtest(self, servers):
        speedtester = speedtest.Speedtest()
        speedtester.get_servers(servers)
        speedtester.get_best_server()
        speedtester.download(threads=None)
        speedtester.upload(threads=None)
        return speedtester.results.dict()

    async def client_ready(self, client, db):
        self.client = client
