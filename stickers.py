from .. import loader, utils

import logging
import warnings
import itertools
import asyncio
import io
from string import hexdigits

from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

try:
    import lottie
except OSError:
    logger.exception("Lottie not available")

warnings.simplefilter("error", Image.DecompressionBombWarning)


@loader.tds
class StickersMod(loader.Module):
    """Tasks with stickers"""
    strings = {"name": "Stickers",
               "stickers_username_cfg_doc": "Bot to use to create stickers",
               "sticker_size_cfg_doc": "The size of one sticker",
               "default_sticker_emoji_cfg_doc": "The emoji to use for stickers by default",
               "what_pack": "<b>You must specify which pack you would like to add the sticker to</b>",
               "what_photo": "<b>Reply to a sticker or photo to add it to your sticker pack</b>",
               "not_animated_pack": "<b>Animated stickers can only be added to animated packs</b>",
               "internal_error": "<b>Something went wrong while adding the sticker</b>",
               "bad_emojis": "<b>The emoji(s) you gave are invalid</b>",
               "animated_pack": "<b>Non-animated stickers cannot be added to animated packs</b>",
               "new_pack": "<b>Create a sticker pack first</b>",
               "pack_full": "<b>That pack is full. Delete some stickers or try making a new pack</b>",
               "added": "<b>Sticker added to</b> <a href='{}'>pack</a><b>!</b>",
               "bad_animated_sticker": "<b>Reply to an animated sticker to convert to a GIF</b>"}

    def __init__(self):
        self.config = loader.ModuleConfig("STICKERS_USERNAME", "Stickers",
                                          lambda m: self.strings("stickers_username_cfg_doc", m),
                                          "STICKER_SIZE", (512, 512), lambda m: self.strings("sticker_size_cfg_doc", m),
                                          "DEFAULT_STICKER_EMOJI", u"🤔",
                                          lambda m: self.strings("default_sticker_emoji_cfg_doc", m))
        self._lock = asyncio.Lock()

    async def kangcmd(self, message):
        args = utils.get_args(message)
        if len(args) not in (1, 2):
            logger.debug("wrong args len(%s) or bad args(%s)", len(args), args)
            await utils.answer(message, self.strings("what_pack", message))
            return

        if not message.is_reply:
            if message.sticker or message.photo:
                logger.debug("user sent photo/sticker directly not reply")
                sticker = message
            else:
                logger.debug("user didnt send any sticker/photo or reply")
                async for sticker in message.client.iter_messages(message.to_id, 10):
                    if sticker.sticker or sticker.photo:
                        break  # Changes message into the right one
        else:
            sticker = await message.get_reply_message()
        if not (sticker.sticker or sticker.photo):
            await utils.answer(message, self.strings("what_photo", message))
            return
        logger.debug("user did send photo/sticker")
        if len(args) > 1:
            emojis = args[1]
        elif sticker.sticker:
            emojis = sticker.file.emoji
        else:
            emojis = None
        if not emojis:
            emojis = self.config["DEFAULT_STICKER_EMOJI"]
        logger.debug(emojis)
        animated = sticker.file.mime_type == "application/x-tgsticker"
        try:
            img = BytesIO()
            await sticker.download_media(file=img)
            img.seek(0)
            logger.debug(img)
            if animated:
                async with self._lock:
                    conv = message.client.conversation("t.me/" + self.config["STICKERS_USERNAME"],
                                                       timeout=5, exclusive=True)
                    async with conv:
                        first = await conv.send_message("/cancel")
                        await conv.get_response()
                        await conv.send_message("/addsticker")
                        buttons = (await conv.get_response()).buttons
                        if buttons is not None:
                            logger.debug("there are buttons, good")
                            button = click_buttons(buttons, args[0])
                            await button.click()
                        else:
                            logger.warning("there's no buttons!")
                            await message.client.send_message("t.me/" + self.config["STICKERS_USERNAME"], "/cancel")
                            await utils.answer(message, "Something went wrong")
                            return
                        # We have sent the pack we wish to modify.
                        # Upload sticker
                        r0 = await conv.get_response()
                        if ".PSD" in r0.message:
                            logger.error("bad response from stickerbot 0")
                            logger.error(r0)
                            await utils.answer(message, self.strings("not_animated_pack", message))
                            msgs = []
                            async for msg in message.client.iter_messages(entity="t.me/"
                                                                          + self.config["STICKERS_USERNAME"],
                                                                          min_id=first.id, reverse=True):
                                msgs += [msg.id]
                            logger.debug(msgs)
                            await message.client.delete_messages("t.me/" + self.config["STICKERS_USERNAME"],
                                                                 msgs + [first])
                            return
                        uploaded = await message.client.upload_file(img, file_name="AnimatedSticker.tgs")
                        m1 = await conv.send_file(uploaded, force_document=False)
                        m2 = await conv.send_message(emojis)
                        await conv.send_message("/done")
                        # Block now so that we mark it all as read
                        await message.client.send_read_acknowledge(conv.chat_id)
                        r1 = await conv.get_response(m1)
                        r2 = await conv.get_response(m2)
                        if "/done" not in r2.message:
                            # That's an error
                            logger.error("Bad response from StickerBot 1")
                            logger.error(r0)
                            logger.error(r1)
                            logger.error(r2)
                            await utils.answer(message, self.strings("internal_error", message))
                            return
                    msgs = []
                    async for msg in message.client.iter_messages(entity="t.me/" + self.config["STICKERS_USERNAME"],
                                                                  min_id=first.id,
                                                                  reverse=True):
                        msgs += [msg.id]
                    logger.debug(msgs)
                    await message.client.delete_messages("t.me/" + self.config["STICKERS_USERNAME"], msgs + [first])
                if "emoji" in r2.message:
                    # The emoji(s) are invalid.
                    logger.error("Bad response from StickerBot 2")
                    logger.error(r2)
                    await utils.answer(message, self.strings("bad_emojis", message))
                    return

            else:
                try:
                    thumb = BytesIO()
                    task = asyncio.ensure_future(utils.run_sync(resize_image, img, self.config["STICKER_SIZE"], thumb))
                    thumb.name = "sticker.png"
                    async with self._lock:
                        conv = message.client.conversation("t.me/" + self.config["STICKERS_USERNAME"],
                                                           timeout=5, exclusive=True)
                        async with conv:
                            first = await conv.send_message("/cancel")
                            await conv.get_response()
                            await conv.send_message("/addsticker")
                            r0 = await conv.get_response()
                            buttons = r0.buttons
                            if buttons is not None:
                                logger.debug("there are buttons, good")
                                button = click_buttons(buttons, args[0])
                                m0 = await button.click()
                            elif "/newpack" in r0.message:
                                await utils.answer(message, self.strings("new_pack", message))
                                return
                            else:
                                logger.warning("there's no buttons!")
                                m0 = await message.client.send_message("t.me/" + self.config["STICKERS_USERNAME"],
                                                                       "/cancel")
                                await utils.answer(message, self.strings("internal_error", message))
                                return
                            # We have sent the pack we wish to modify.
                            # Upload sticker
                            r0 = await conv.get_response()
                            if ".TGS" in r0.message:
                                logger.error("bad response from stickerbot 0")
                                logger.error(r0)
                                await utils.answer(message, self.strings("animated_pack", message))
                                msgs = []
                                async for msg in message.client.iter_messages(entity="t.me/"
                                                                              + self.config["STICKERS_USERNAME"],
                                                                              min_id=first.id,
                                                                              reverse=True):
                                    msgs += [msg.id]
                                logger.debug(msgs)
                                await message.client.delete_messages("t.me/" + self.config["STICKERS_USERNAME"],
                                                                     msgs + [first])
                                return
                            if "120" in r0.message:
                                logger.error("bad response from stickerbot 0")
                                logger.error(r0)
                                await utils.answer(message, self.strings("pack_full", message))
                                msgs = []
                                async for msg in message.client.iter_messages(entity="t.me/"
                                                                              + self.config["STICKERS_USERNAME"],
                                                                              min_id=first.id,
                                                                              reverse=True):
                                    if msg.id != m0.id:
                                        msgs += [msg.id]
                                logger.debug(msgs)
                                await message.client.delete_messages("t.me/" + self.config["STICKERS_USERNAME"],
                                                                     msgs + [first])
                                return
                            await task  # We can resize the thumbnail while the sticker bot is processing other data
                            thumb.seek(0)
                            m1 = await conv.send_file(thumb, allow_cache=False, force_document=True)
                            r1 = await conv.get_response(m1)
                            m2 = await conv.send_message(emojis)
                            r2 = await conv.get_response(m2)
                            if "/done" in r2.message:
                                await conv.send_message("/done")
                            else:
                                logger.error(r1)
                                logger.error(r2)
                                logger.error("Bad response from StickerBot 0")
                                await utils.answer(message, self.strings("internal_error", message))
                            await message.client.send_read_acknowledge(conv.chat_id)
                            if "/done" not in r2.message:
                                # That's an error
                                logger.error("Bad response from StickerBot 1")
                                logger.error(r1)
                                logger.error(r2)
                                await utils.answer(message, self.strings("internal_error", message))
                                return
                            msgs = []
                            async for msg in message.client.iter_messages(entity="t.me/"
                                                                          + self.config["STICKERS_USERNAME"],
                                                                          min_id=first.id,
                                                                          reverse=True):
                                msgs += [msg.id]
                        logger.debug(msgs)
                        await message.client.delete_messages("t.me/" + self.config["STICKERS_USERNAME"], msgs + [first])
                        if "emoji" in r2.message:
                            # The emoji(s) are invalid.
                            logger.error("Bad response from StickerBot 2")
                            logger.error(r2)
                            await utils.answer(message, self.strings("bad_emojis", message))
                            return
                finally:
                    thumb.close()
        finally:
            img.close()
        packurl = utils.escape_html("https://t.me/addstickers/{}".format(button.text))
        await utils.answer(message, self.strings("added", message).format(packurl))

    async def filecmd(self, message):
        await convert(message)


async def convert(message, as_file=True):
    reply = await message.get_reply_message()
    if not reply or not reply.sticker:
        await message.edit("<b>Reply to sticker!</b>")
        return
    fname = reply.sticker.attributes[-1].file_name
    if ".tgs" in fname:
        await message.edit("<b>Reply to not animated sticker!</b>")
        return
    bg = (0, 0, 0, 0)
    args = utils.get_args(message)
    if args:
        args = args[0]
        if args.startswith("#"):
            for ch in args[1:]:
                if ch not in hexdigits:
                    break
            bg = args

    im = io.BytesIO()
    await message.client.download_file(reply, im)
    im = Image.open(im)
    img = Image.new("RGBA", im.size, bg)
    if im.mode == "RGBA":
        img.paste(im, (0, 0), im)
    else:
        img.paste(im, (0, 0))
    out = io.BytesIO()
    out.name = fname + ".png"
    img.save(out, "PNG")
    out.seek(0)
    await message.delete()
    await message.client.send_file(message.to_id, out, force_document=as_file, reply_to=reply)

def click_buttons(buttons, target_pack):
    buttons = list(itertools.chain.from_iterable(buttons))
    # Process in reverse order; most difficult to match first
    try:
        return buttons[int(target_pack)]
    except (IndexError, ValueError):
        pass
    logger.debug(buttons)
    for button in buttons:
        logger.debug(button)
        if button.text == target_pack:
            return button
    for button in buttons:
        if target_pack in button.text:
            return button
    for button in buttons:
        if target_pack.lower() in button.text.lower():
            return button
    return buttons[-1]


def resize_image(img, size, dest):
    # Wrapper for asyncio purposes
    try:
        im = Image.open(img)
        # We used to use thumbnail(size) here, but it returns with a *max* dimension of 512,512
        # rather than making one side exactly 512 so we have to calculate dimensions manually :(
        if im.width == im.height:
            size = (512, 512)
        elif im.width < im.height:
            size = (int(512 * im.width / im.height), 512)
        else:
            size = (512, int(512 * im.height / im.width))
        logger.debug("Resizing to %s", size)
        im.resize(size).save(dest, "PNG")
    finally:
        im.close()
        img.close()
        del im
