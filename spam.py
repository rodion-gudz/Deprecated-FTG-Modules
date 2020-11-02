from .. import loader, utils
import logging
import asyncio


logger = logging.getLogger(__name__)


@loader.tds
class SpamMod(loader.Module):
    """Annoys people really effectively"""
    strings = {"name": "Spam"}

    async def spamcmd(self, message):
        """.spam <count> <message>"""
        use_reply = False
        args = utils.get_args(message)
        logger.debug(args)
        reply = await message.get_reply_message()
        if reply:
            if reply.media:
                media = reply.media
                count = int(args[0].strip())
                await message.delete()
                for _ in range(count):
                    await message.client.send_file(message.to_id, media)
                return
            else:
                text = reply
                count = int(args[0].strip())
                for _ in range(count):
                    await message.client.send_message(message.to_id, text)

