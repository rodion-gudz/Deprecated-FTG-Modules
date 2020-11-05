from .. import loader, utils

import asyncio
import logging
logger = logging.getLogger(__name__)

class CalculatorMod(loader.Module):
    strings = {'name': 'Python'}

    async def calccmd(self, message):
        question = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not question:
            if not reply:
                await utils.answer(message, "<b>2+2=5</b>")
                return
            else:
                question = reply.raw_text
        try:
            answer = eval(question)
            answer = f"<b>{question}=</b><code>{answer}</code>"
        except Exception as e:
            answer = f"<b>{question}=</b><code>{e}</code>"
        await utils.answer(message, answer)

    def __init__(self):
        self.config = loader.ModuleConfig(
            "msg_format", "{0}", "Format of each message. {0} replaces current number.",
            "default_delay", 1.0, "Delay in all commands by default"
        )
        self.name = self.strings['name']

    def config_complete(self):
        self.name = self.strings['name']

    async def _do_range(self, range_args, delay, message):
        """for internal usage; do range itself"""
        await message.delete()
        for now in range(*range_args):
            await message.respond(self.config['msg_format'].format(now))
            await asyncio.sleep(delay)

    async def _get_args(self, message, minn, maxn):
        args = utils.get_args(message)
        if len(args) < minn:
            logger.warning(f'Minimum {minn} {"args" if minn != 1 else "arg"}, {len(args)} provided')
            await utils.answer(message, self.strings['no_args'].format(minn))
            return None
        elif len(args) > maxn:
            logger.warning(f'Maximum {maxn} {"args" if maxn != 1 else "arg"}, {len(args)} provided')
            await utils.answer(message, self.strings['many_args'].format(maxn))
            return None
        return args

    async def _check_range_args(self, range_args, message):
        """for internal usage; check if range args are int"""
        try:
            range_args = [int(x) for x in range_args]
            return range_args
        except ValueError:
            logger.warning(f'Impossible to convert all range args to int ({range_args})')
            await utils.answer(message, self.strings['args_int'])
            return None

    async def rangecmd(self, message):
        args = await self._get_args(message, 1, 3)
        if args is None:
            return  # user done sth wrong

        delay = self.config['default_delay']
        range_args = await self._check_range_args(args, message)
        if range_args is None:
            return  # user done sth wrong

        await self._do_range(range_args, delay, message)

    async def drangecmd(self, message):
        args = await self._get_args(message, 2, 4)
        if args is None:
            return  # user done sth wrong

        try:
            delay = float(args[0])
        except ValueError:
            logger.warning(f'Impossible to convert delay to float ({args[0]})')
            await utils.answer(message, self.strings['delay_num'])
            return

        range_args = await self._check_range_args(args[1:], message)
        if range_args is None:
            return

        await self._do_range(range_args, delay, message)

    async def countcmd(self, message):
        args = await self._get_args(message, 1, 2)
        if args is None:
            return

        if len(args) == 1:
            delay = self.config['default_delay']
            range_args = (1, args[0], 1)
        elif len(args) == 2:
            try:
                delay = float(args[0])
            except ValueError:
                logger.warning(f'Impossible to convert delay to float ({args[0]})')
                await utils.answer(message, self.strings['delay_num'])
                return
            range_args = (1, args[1], 1)

        range_args = await self._check_range_args(range_args, message)
        if range_args is None:
            return
        range_args[1] += 1  # so last number we print will be N itself

        await self._do_range(range_args, delay, message)

    async def rcountcmd(self, message):
        args = await self._get_args(message, 1, 2)
        if args is None:
            return

        if len(args) == 1:
            delay = self.config['default_delay']
            range_args = (args[0], 0, -1)
        elif len(args) == 2:
            try:
                delay = float(args[0])
            except ValueError:
                logger.warning(f'Impossible to convert delay to float ({args[0]})')
                await utils.answer(message, self.strings['delay_num'])
                return
            range_args = (args[1], 0, -1)

        range_args = await self._check_range_args(range_args, message)
        if range_args is None:
            return

        await self._do_range(range_args, delay, message)

