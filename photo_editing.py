import glob, os
from random import randint, uniform
from PIL import Image, ImageEnhance, ImageOps
from telethon.tl.types import DocumentAttributeFilename
from PIL import Image, ImageFilter
from PIL import Image, ImageDraw, ImageEnhance
import PIL.ImageOps
import re
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
import string
import random
from PIL import Image, ImageDraw
import asyncio
import logging
from asyncio import sleep
from telethon import functions, types
from .. import loader, utils
import io

_C = 'png'
_B = 'name'
_A = 'image'
_R = 'отражает'
_P = 'часть.'
from .. import loader as _L, utils as U
from telethon.tl.types import DocumentAttributeFilename as DAF
from PIL import Image, ImageOps as IO
from io import BytesIO as ist


# Author: https://t.me/GovnoCodules and https://t.me/memeframe

@loader.tds
class DistortMod(loader.Module):
    strings = {"name": "Picture editor"}
    f'{_R} фоточки'

    def __init__(A):
        A.name = A.strings[_B]

    async def llcmd(A, message):
        await KZD(message, 1)

    async def rrcmd(A, message):
        await KZD(message, 2)

    async def uucmd(A, message):
        await KZD(message, 3)

    async def ddcmd(A, message):
        await KZD(message, 4)

    async def delbgcmd(self, m):
        """Удалить белый фон(всё что >230)
        Возвращает стикер webp
        Если после команды что-либо указать, отправится как файл png"""
        s = "[ImageManager -> DelBg]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        im2 = Image.open(im).convert("RGBA")
        w, h = im2.size
        for x in range(w):
            for y in range(h):
                if im2.getpixel((x, y)) >= (230, 230, 230):
                    im2.putpixel((x, y), (0, 0, 0, 0))
        output = io.BytesIO()
        as_file = bool(utils.get_args_raw(m))
        output.name = "delbg." + ("png" if as_file else "webp")
        if not as_file:
            im2.thumbnail((512, 512))
        im2.save(output)
        output.seek(0)
        del im2
        await m.client.send_file(m.to_id, output, force_document=as_file, reply_to=reply.id)
        await m.delete()

    async def delbg2cmd(self, m):
        """Удалить черный фон(всё что <30)
        Возвращает стикер webp
        Если после команды что-либо указать, отправится как файл png"""
        s = "[ImageManager -> DelBg]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        im2 = Image.open(im).convert("RGBA")
        w, h = im2.size
        for x in range(w):
            for y in range(h):
                if im2.getpixel((x, y)) <= (30, 30, 30):
                    im2.putpixel((x, y), (0, 0, 0, 0))
        output = io.BytesIO()
        as_file = bool(utils.get_args_raw(m))
        output.name = "delbg." + ("png" if as_file else "webp")
        if not as_file:
            im2.thumbnail((512, 512))
        im2.save(output)
        output.seek(0)
        del im2
        await m.client.send_file(m.to_id, output, force_document=as_file, reply_to=reply.id)
        await m.delete()

    async def resizecmd(self, m):
        """<x:int> <y:int>
        Изменить размер фото"""
        s = "[ImageManager -> Resize]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <x:int> <y:int>")
            return
        rr = re.compile(r"^(\d+)\s+(\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <x:int> <y:int>")
            return
        x = int(rr.findall(args)[0][0])
        y = int(rr.findall(args)[0][1])
        await m.edit(s + "Работаю...")
        im2 = Image.open(im)
        im2 = im2.resize((x, y))
        out = io.BytesIO()
        iswebp = True if reply.file.ext == ".webp" else False
        if iswebp:
            im2.thumbnail((512, 512))
        out.name = "resized." + (".webp" if iswebp else ".png")
        im2.save(out)
        out.seek(0)
        await m.client.send_file(m.to_id, out, reply_to=reply.id)
        await m.delete()

    async def rotatecmd(self, m):
        """<rotate:int>
        Повернуть изображение"""
        s = "[ImageManager -> Rotate]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <rotate:int>")
            return
        rr = re.compile(r"^(-*\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <rotate:int>")
            return
        c = int(rr.findall(args)[0])
        im2 = Image.open(im)
        im2 = im2.rotate(c, expand=True)
        out = io.BytesIO()
        iswebp = True if reply.file.ext == ".webp" else False
        if iswebp:
            im2.thumbnail((512, 512))
        out.name = "rotate." + (".webp" if iswebp else ".png")
        im2.save(out)
        out.seek(0)
        await m.client.send_file(m.to_id, out, reply_to=reply.id)
        await m.delete()

    async def invertcmd(self, m):
        """Инвертировать цвета фото"""
        s = "[ImageManager -> Invert]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        await m.client.send_file(m.to_id, await invert_image(im, reply.file.ext), reply_to=reply.id)
        await m.delete()

    async def contrstcmd(self, m):
        """<level:float or int>
        Изменить контрастность изображения"""
        s = "[ImageManager -> Contrast]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <level:float or int>")
            return
        rr = re.compile(r"^(\d+|\d+\.\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <level:float or int>")
            return
        c = float(rr.findall(args)[0])
        await m.client.send_file(m.to_id, await contrast(im, c, reply.file.ext), reply_to=reply.id)
        await m.delete()

    async def convpcmd(self, m):
        """Стикер в фото
        Фото в стикер"""
        s = "[ImageManager -> Converter]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        im2 = Image.open(im)
        iswebp = True if reply.file.ext == ".webp" else False
        out = io.BytesIO()
        if iswebp:
            out.name = "conv.png"
        else:
            im2.thumbnail((512, 512))
            out.name = "conv.webp"
        im2.save(out)
        out.seek(0)
        await m.client.send_file(m.to_id, out, reply_to=reply.id)
        await m.delete()

    async def brightcmd(self, m):
        """<level:float or int>
        Изменить яркость фото"""
        s = "[ImageManager -> Bright]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <level:float or int>")
            return
        rr = re.compile(r"^(\d+|\d+\.\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <level:float or int>")
            return
        c = float(rr.findall(args)[0])
        await m.client.send_file(m.to_id, setbright(im, c, reply.file.ext), reply_to=reply.id)
        await m.delete()

    async def sharpnesscmd(self, m):
        """<level:float or int>
        Изменить чёткость фото(если указать много, будет deepfry)"""
        s = "[ImageManager -> Sharpness]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <level:float or int>")
            return
        rr = re.compile(r"^(\d+|\d+\.\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <level:float or int>")
            return
        c = float(rr.findall(args)[0])
        await m.client.send_file(m.to_id, setsharpness(im, c, reply.file.ext), reply_to=reply.id)
        await m.delete()

    async def pic2packcmd(self, message):

        reply = await message.get_reply_message()
        if not reply:
            await message.edit("<b>Reply to photo❗</b>")
            return

        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Packname</b>❓")
            return
        chat = '@Stickers'
        name = "".join([random.choice(list(string.ascii_lowercase + string.ascii_uppercase)) for _ in range(16)])
        emoji = "▫️"
        image = io.BytesIO()
        await message.client.download_file(reply, image)
        image = Image.open(image)
        w, h = image.size
        www = max(w, h)
        await message.edit("🔪<b>Cropping...</b>")
        img = Image.new("RGBA", (www, www), (0, 0, 0, 0))
        img.paste(image, ((www - w) // 2, 0))
        face = img.resize((100, 100))
        fface = io.BytesIO()
        fface.name = name + ".png"
        images = await cropping(img)
        face.save(fface)
        fface.seek(0)
        await message.edit("<b>📤Uploading...</b>")
        async with message.client.conversation(chat) as conv:
            try:
                x = await message.client.send_message(chat, "/cancel")
                await (await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))).delete()
                await x.delete()
                x = await message.client.send_message(chat, "/newpack")
                await (await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))).delete()
                await x.delete()
                x = await message.client.send_message(chat, args)
                await (await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))).delete()
                await x.delete()

                for im in images:
                    blank = io.BytesIO(im)
                    blank.name = name + ".png"
                    blank.seek(0)
                    x = await message.client.send_file(chat, blank, force_document=True)
                    await (await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))).delete()
                    await x.delete()
                    x = await message.client.send_message(chat, emoji)
                    await (await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))).delete()
                    await x.delete()

                x = await message.client.send_message(chat, "/publish")
                await (await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))).delete()
                await x.delete()
                x = await message.client.send_file(chat, fface, force_document=True)
                await (await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))).delete()
                await x.delete()
                x = await message.client.send_message(chat, name)
                ending = await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))
                await x.delete()
                await ending.delete()
                for part in ending.raw_text.split():
                    if part.startswith("https://t.me/"):
                        break
                await message.edit('✅<b>Uploaded successful!</b>\n' + part)

            except YouBlockedUserError:
                await message.edit('<b>@Stickers BLOCKED⛔</b>')
                return

    async def deepcmd(self, message):
        try:
            frycount = int(utils.get_args(message)[0])
            if frycount < 1:
                raise ValueError
        except:
            frycount = 1

        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)

            if isinstance(data, bool):
                await message.edit("Reply to photo please")
                return
        else:
            await message.edit("Reply to photo please")
            return

        await message.edit("Downloading...")
        image = io.BytesIO()
        await message.client.download_media(data, image)
        image = Image.open(image)

        await message.edit("Distorting...")
        for _ in range(frycount):
            image = await deepfry(image)

        fried_io = io.BytesIO()
        fried_io.name = "image.jpeg"
        image.save(fried_io, "JPEG")
        fried_io.seek(0)
        await message.delete()
        await message.reply(file=fried_io)

    async def distortcmd(self, message):
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await message.edit("Error")
                return
        else:
            await message.edit("Error")
            return
        await message.edit("Distorting...")
        for distorted in glob.glob("distorted*"):
            os.remove(distorted)
        for findistorted in glob.glob("*/distorted*"):
            os.remove(findistorted)

        fname = f"distorted{random.randint(1, 100)}.png"

        with open(fname, "wb") as file:
            file.write(await message.client.download_media(data, bytes))
        image = Image.open(fname)
        image.save(fname)
        imgdimens = image.width, image.height
        distortcmd = f"convert {fname} -liquid-rescale 60x60%! -resize {imgdimens[0]}x{imgdimens[1]}\! {fname}"
        os.system(distortcmd)
        image = Image.open(f"{fname}")
        buf = io.BytesIO()
        buf.name = 'image.png'
        image.save(buf, 'PNG')
        buf.seek(0)
        await message.edit("Sending...")
        await message.client.send_file(message.chat_id, buf, reply_to=reply_message.id)
        await message.delete()

    async def linescmd(self, message):
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("reply to photo")
            return
        try:
            photo = reply.media.photo
        except:
            await message.edit("reply to photo only")
            return

        chat = '@Lines50Bot'
        await message.edit('@Lines50Bot <code>in process...</code>')
        async with message.client.conversation(chat) as conv:
            try:
                response = conv.wait_event(events.NewMessage(incoming=True, from_users=1120861844))
                response2 = conv.wait_event(events.NewMessage(incoming=True, from_users=1120861844))
                mm = await message.client.send_file(chat, photo)
                response = await response
                response2 = await response2
                await mm.delete()
            except YouBlockedUserError:
                await message.reply('<code>Unblock</code> @Lines50Bot')
                return

            await message.delete()
            await message.client.send_file(message.to_id, response2.media)
            await response.delete()
            await response2.delete()
            await message.client(functions.messages.DeleteHistoryRequest(
                peer='Lines50Bot',
                max_id=0,
                just_clear=False,
                revoke=True
            ))

    async def jpegdcmd(self, message):
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await message.delete()
                return
        else:
            await message.delete()
            return

        image = io.BytesIO()
        await message.client.download_media(data, image)
        image = Image.open(image)
        fried_io = io.BytesIO()
        fried_io.name = "image.jpeg"
        image = image.convert("RGB")
        image.save(fried_io, "JPEG", quality=0)
        fried_io.seek(0)
        await message.delete()
        await message.client.send_file(message.chat_id, fried_io, reply_to=reply_message.id)

    async def maccmd(S, message):
        R = True
        Q = 'image'
        P = '/'
        L = 'RGBA'
        K = '<b>Image?</b>'
        A = message
        C = await A.get_reply_message()
        B = io.BytesIO()
        M = None
        if A.file:
            if A.file.mime_type.split(P)[0] == Q:
                await A.download_media(B)
            elif C:
                if C.file:
                    if C.file.mime_type.split(P)[0] == Q: M = R;await C.download_media(B)
                else:
                    await A.edit(K);
                    return
            else:
                await A.edit(K);
                return
        elif C:
            if C.file:
                if C.file.mime_type.split(P)[0] == Q: M = R;await C.download_media(B)
            else:
                await A.edit(K);
                return
        else:
            await A.edit(K);
            return
        try:
            I = Image.open(B)
        except:
            await A.edit(K);
            return
        await A.edit('<b>Working...</b>');
        F, G = I.size;
        B = Image.new(L, (F, G));
        J = min(F // 100, G // 100);
        D = Image.new(L, (F + J * 40, G + J * 40), '#fff')
        if I.mode == L:
            B.paste(I, (0, 0), I);
            E = Image.new(L, (F, G))
            for N in range(F):
                for O in range(G):
                    if B.getpixel((N, O)) != (0, 0, 0, 0): E.putpixel((N, O), (0, 0, 0))
        else:
            B.paste(I, (0, 0));
            E = Image.new(L, (F, G), 'black')
        E = E.resize((F + J * 5, G + J * 5));
        D.paste(E, ((D.width - E.width) // 2, (D.height - E.height) // 2), E);
        D = D.filter(ImageFilter.GaussianBlur(J * 5));
        D.paste(B, ((D.width - B.width) // 2, (D.height - B.height) // 2), B);
        H = io.BytesIO();
        H.name = '-'.join(
            [''.join([random.choice(string.hexdigits) for B in range(A)]) for A in [5, 4, 3, 2, 1]]) + '.png';
        D.save(H, 'PNG');
        H.seek(0)
        if utils.get_args_raw(A):
            await A.client.send_file(A.to_id, H, force_document=R);
            await A.delete()
        elif M:
            await C.reply(file=H);
            await A.delete()
        else:
            await A.edit(file=H, text='')

    async def rotatecmd(self, message):
        global angle
        try:
            angle = int(utils.get_args(message)[0])
        except:
            angle = 180

        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)

            if isinstance(data, bool):
                await message.edit("`I can't rotate that!".upper())
                return
        else:
            await message.edit("Reply to an image or sticker to rotate it!".upper())
            return

        image = io.BytesIO()
        await message.client.download_media(data, image)
        image = Image.open(image)

        try:
            image = image.rotate(angle, expand=True)
        except Exception as e:
            await message.edit("ERROR IN ROTATE\n" + str(e))
            return
        await message.delete()
        image_stream = io.BytesIO()
        image_stream.name = "pilrotate.png"
        image.save(image_stream, "PNG")
        image_stream.seek(0)
        await message.client.send_file(message.chat_id, image_stream)

    async def gridcmd(self, message):
        """.gird <reply to photo>"""
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await utils.answer(message, "<code>Реплай на пикчу или стикер блять!</code>")
                return
        else:
            await utils.answer(message, "`Реплай на пикчу или стикер блять`")
            return

        await message.edit("Режу ебать")
        file = await message.client.download_media(data, bytes)
        media = await griding(file)
        await message.delete()
        await message.client.send_file(message.to_id, media)

    async def revgridcmd(self, message):
        """.gird <reply to photo>"""
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await utils.answer(message, "<code>Реплай на пикчу или стикер блять!</code>")
                return
        else:
            await utils.answer(message, "`Реплай на пикчу или стикер блять`")
            return

        await message.edit("Режу ебать")
        file = await message.client.download_media(data, bytes)
        media = await griding(file)
        media = media[::-1]
        await message.delete()
        await message.client.send_file(message.to_id, media)

    async def opscmd(self, message):
        way = utils.get_args(message)
        if not way:
            return
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)

            if isinstance(data, bool):
                await message.edit("`I can't ops that!".upper())
                return
        else:
            await message.edit("Reply to an image or sticker to ops it!".upper())
            return

        image = io.BytesIO()
        await message.client.download_media(data, image)
        image = Image.open(image)

        if "m" in way:
            try:
                image = ImageOps.mirror(image)
            except Exception as e:
                await message.edit("ERROR IN MIRROR\n" + str(e))
                return
        if "f" in way:
            try:
                image = ImageOps.flip(image)
            except Exception as e:
                await message.edit("ERROR IN FLIP\n" + str(e))
                return

        await message.delete()
        image_stream = io.BytesIO()
        image_stream.name = "pilops.png"
        image.save(image_stream, "PNG")
        image_stream.seek(0)
        await message.client.send_file(message.chat_id, image_stream)

    @loader.sudo
    async def spincmd(self, message):
        args = utils.get_args(message)

        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await utils.answer(message, "Reply to picture")
                return
        else:
            await utils.answer(message, "Reply to picture")
            return

        image = io.BytesIO()
        await message.client.download_media(data, image)
        image = Image.open(image)
        image.thumbnail((512, 512), Image.ANTIALIAS)
        img = Image.new("RGB", (512, 512), "black")
        img.paste(image, ((512 - image.width) // 2, (512 - image.height) // 2))
        image = img
        way = random.choice([1, -1])
        frames = []
        for i in range(1, 60):
            im = image.rotate(i * 6 * way)
            frames.append(im)
        frames.remove(im)

        image_stream = io.BytesIO()
        image_stream.name = "new.gif"
        im.save(image_stream, "GIF", save_all=True, append_images=frames, duration=10)
        image_stream.seek(0)
        await utils.answer(message, image_stream)

    @loader.sudo
    async def epilepsycmd(self, message):
        args = utils.get_args(message)

        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await utils.answer(message, "Reply to picture")
                return
        else:
            await utils.answer(message, "Reply to picture")
            return

        image = io.BytesIO()
        await message.client.download_media(data, image)
        image = Image.open(image).convert("RGB")
        invert = ImageOps.invert(image)

        image_stream = io.BytesIO()
        image_stream.name = "new.gif"
        image.save(image_stream, "GIF", save_all=True, append_images=[invert], duration=1)
        image_stream.seek(0)
        await utils.answer(message, image_stream)

    async def resizecmd(self, message):
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)

            if isinstance(data, bool):
                await message.edit("`I can't resize that!".upper())
                return
        else:
            await message.edit("Reply to an image or sticker to resize it!".upper())
            return
        uinp = utils.get_args(message)

        if not uinp:
            await message.edit("What's about input".upper())
            return
        image = io.BytesIO()
        await message.client.download_media(data, image)
        image = Image.open(image)
        x, y = image.size
        rx, ry = None, None
        if len(uinp) == 1:
            try:
                rx, ry = int(uinp[0]), int(uinp[0])
            except ValueError:
                if uinp[0] == "x":
                    rx, ry = x, x
                if uinp[0] == "y":
                    rx, ry = y, y
                else:
                    await message.edit("INPUT MUST BE STING")
                    return
        else:
            if uinp[0] == "x":
                rx = x
            if uinp[0] == "y":
                rx = y
            if uinp[1] == "x":
                ry = x
            if uinp[1] == "y":
                ry = y
            if not rx:
                try:
                    rx = int(uinp[0])
                except:
                    await message.edit("ERROR IN INPUT")
                    return
            if not ry:
                try:
                    ry = int(uinp[1])
                except:
                    await message.edit("ERROR IN INPUT")
                    return

        try:
            image = image.resize((rx, ry))
        except Exception as e:
            await message.edit("ERROR IN RESIZE\n" + str(e))
            return
        await message.delete()
        image_stream = io.BytesIO()
        image_stream.name = "pilresize.png"
        image.save(image_stream, "PNG")
        image_stream.seek(0)
        await message.client.send_file(message.chat_id, image_stream)

    async def sl2rcmd(self, message):
        """swipe left to right"""
        await presser(message, 0)

    @loader.owner
    async def sr2lcmd(self, message):
        """swipe right to left"""
        await presser(message, 1)

    @loader.owner
    async def su2dcmd(self, message):
        """swipe up to down"""
        await presser(message, 2)

    @loader.owner
    async def sd2ucmd(self, message):
        """swipe down to up"""
        await presser(message, 3)

    async def resizedoccmd(self, message):
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)

            if isinstance(data, bool):
                await message.edit("`I can't resize that!".upper())
                return
        else:
            await message.edit("Reply to an image or sticker to resize it!".upper())
            return
        uinp = utils.get_args(message)

        if not uinp:
            await message.edit("What's about input".upper())
            return
        image = io.BytesIO()
        await message.client.download_media(data, image)
        image = Image.open(image)
        x, y = image.size
        rx, ry = None, None
        if len(uinp) == 1:
            try:
                rx, ry = int(uinp[0]), int(uinp[0])
            except ValueError:
                if uinp[0] == "x":
                    rx, ry = x, x
                if uinp[0] == "y":
                    rx, ry = y, y
                else:
                    await message.edit("INPUT MUST BE STING")
                    return
        else:
            if uinp[0] == "x":
                rx = x
            if uinp[0] == "y":
                rx = y
            if uinp[1] == "x":
                ry = x
            if uinp[1] == "y":
                ry = y
            if not rx:
                try:
                    rx = int(uinp[0])
                except:
                    await message.edit("ERROR IN INPUT")
                    return
            if not ry:
                try:
                    ry = int(uinp[1])
                except:
                    await message.edit("ERROR IN INPUT")
                    return

        try:
            image = image.resize((rx, ry))
        except Exception as e:
            await message.edit("ERROR IN RESIZE\n" + str(e))
            return
        await message.delete()
        image_stream = io.BytesIO()
        image_stream.name = "pilresize.png"
        image.save(image_stream, "PNG")
        image_stream.seek(0)
        await message.client.send_file(message.chat_id, image_stream, force_document=True)

    @loader.unrestricted
    async def dotifycmd(self, message):
        """Image to RGB dots"""
        mode = False
        reply, pix = await parse(message)
        if reply:
            await dotify(message, reply, pix, mode)

    async def dotificmd(self, message):
        """Image to BW dots """
        mode = True
        reply, pix = await parse(message)
        if reply:
            await dotify(message, reply, pix, mode)

    async def soapcmd(self, message):
        soap = 3
        a = utils.get_args(message)
        if a:
            if a[0].isdigit():
                soap = int(a[0])
                if soap <= 0:
                    soap = 3

        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await utils.answer(message, "<code>Reply to pic or stick!</code>")
                return
        else:
            await utils.answer(message, "<code>Reply to pic or stick!</code>")
            return

        await message.edit("Soaping...")
        file = await message.client.download_media(data, bytes)
        media = await Soaping(file, soap)
        await message.delete()

        await message.client.send_file(message.to_id, media)

    async def crosscmd(self, message):
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("<b>А что зачеркнуть?</b>")
            return
        client = message.client
        im = io.BytesIO()
        await client.download_file(reply, im)
        im = Image.open(im)
        width, heigth = im.size
        center = min(width, heigth)
        im = im.crop(((width - center) // 2, (heigth - center) // 2, (width + center) // 2, (heigth + center) // 2))
        line = Image.new("RGBA", (width, heigth // 6), (255, 0, 0, 255))
        line_one = line.rotate(45, expand=True, fillcolor=None).resize(im.size)
        line_two = line.rotate(-45, expand=True, fillcolor=None).resize(im.size)
        line_two.paste(line_one, (0, 0), line_one)
        cross = Image.new("RGBA", im.size, (255, 255, 255, 255))
        cross.paste(line_two, (0, 0), line_two)
        cross.putalpha(150)
        im.paste(cross, (0, 0), cross)
        output = io.BytesIO()
        output.name = "output.png"
        im.save(output)
        output.seek(0)
        await client.send_file(message.to_id, output, reply_to=reply)
        await message.delete()


async def KZD(message, type):
    S = 'sticker';
    A = message;
    N = await A.get_reply_message();
    Q, J = await CM(N)
    if not Q or not N: await A.edit('<b>Реплай на стикер или фото!</b>');return
    O = 'KZD.' + J;
    P = U.get_args_raw(A)
    if P:
        if P in [_A[:A] for A in range(1, len(_A) + 1)]: O = 'KZD.png';J = _C
        if P in [S[:A] for A in range(1, len(S) + 1)]: O = 'KZD.webp';J = 'webp'
    R = ist();
    await A.edit('<b>Извиняюсь...</b>');
    await A.client.download_media(Q, R);
    E = Image.open(R);
    B, C = E.size
    if B % 2 != 0 and type in [1, 2] or C % 2 != 0 and type in [3, 4]: E = E.resize((B + 1, C + 1));C, B = E.size
    if type == 1: D = 0;F = 0;G = B // 2;H = C;K = G;L = D
    if type == 2: D = B // 2;F = 0;G = B;H = C;K = F;L = F
    if type == 3: D = 0;F = 0;G = B;H = C // 2;K = D;L = H
    if type == 4: D = 0;F = C // 2;G = B;H = C;K = D;L = D
    I = E.crop((D, F, G, H))
    if type in [1, 2]:
        I = IO.mirror(I)
    else:
        I = IO.flip(I)
    E.paste(I, (K, L));
    M = ist();
    M.name = O;
    E.save(M, J);
    M.seek(0);
    await A.client.send_file(A.to_id, M, reply_to=N);
    await A.delete()


async def CM(R):
    D = False;
    C = None;
    A = R
    if A and A.media:
        if A.photo:
            B = A.photo;
            E = _C
        elif A.document:
            if DAF(file_name='AnimatedSticker.tgs') in A.media.document.attributes: return D, C
            if A.gif or A.video or A.audio or A.voice: return D, C
            B = A.media.document
            if _A not in B.mime_type: return D, C
            E = B.mime_type.split('/')[1]
        else:
            return D, C
    else:
        return D, C
    if not B or B is C:
        return D, C
    else:
        return B, E


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.gif or reply_message.video or reply_message.audio or reply_message.voice:
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data


async def Soaping(file, soap):
    img = Image.open(io.BytesIO(file))
    (x, y) = img.size
    img = img.resize((x // soap, y // soap), Image.ANTIALIAS)
    img = img.resize((x, y))
    soap_io = io.BytesIO()
    soap_io.name = "image.jpeg"
    img = img.convert("RGB")
    img.save(soap_io, "JPEG", quality=100)
    soap_io.seek(0)
    return soap_io


async def deepfry(img: Image) -> Image:
    colours = (
        (randint(50, 200), randint(40, 170), randint(40, 190)),
        (randint(190, 255), randint(170, 240), randint(180, 250))
    )

    img = img.copy().convert("RGB")

    # Crush image to hell and back
    img = img.convert("RGB")
    width, height = img.width, img.height
    img = img.resize((int(width ** uniform(0.8, 0.9)), int(height ** uniform(0.8, 0.9))), resample=Image.LANCZOS)
    img = img.resize((int(width ** uniform(0.85, 0.95)), int(height ** uniform(0.85, 0.95))), resample=Image.BILINEAR)
    img = img.resize((int(width ** uniform(0.89, 0.98)), int(height ** uniform(0.89, 0.98))), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, randint(3, 7))

    # Generate colour overlay
    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(uniform(1.0, 2.0))
    overlay = ImageEnhance.Brightness(overlay).enhance(uniform(1.0, 2.0))

    overlay = ImageOps.colorize(overlay, colours[0], colours[1])

    # Overlay red and yellow onto main image and sharpen the hell out of it
    img = Image.blend(img, overlay, uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(randint(5, 300))

    return img


async def griding(file):
    img = Image.open(io.BytesIO(file))
    (x, y) = img.size
    cy = 3
    cx = 3
    sx = x // cx
    sy = y // cy
    if (sx * cx, sy * cy) != (x, y):
        img = img.resize((sx * cx, sy * cy))
    (lx, ly) = (0, 0)
    media = []
    for i in range(1, cy + 1):
        for o in range(1, cx + 1):
            mimg = img.crop((lx, ly, lx + sx, ly + sy))
            bio = io.BytesIO()
            bio.name = 'image.png'
            mimg.save(bio, 'PNG')
            media.append(bio.getvalue())
            lx = lx + sx
        lx = 0
        ly = ly + sy
    return media


async def presser(message, way):
    reply = await check_mediaa(message)
    if not reply:
        await message.edit("<b>Senpai... please reply to image or not animated sticker!</b>")
        return
    im = io.BytesIO()
    await reply.download_media(im)
    im = Image.open(im)
    w, h = im.size
    out = []
    await message.edit("<b>Working hard...</b>")
    if way == 0:
        for x in range(1, w, w // 30):
            im1 = im2 = im.copy()
            temp = Image.new("RGB", (w, h))
            im1 = im1.resize((x, h))
            im2 = im2.resize((w - x, h))
            temp.paste(im1, (0, 0))
            temp.paste(im2, (x, 0))
            out.append(temp)

    if way == 1:
        for x in range(1, w, w // 30):
            im1 = im2 = im.copy()
            temp = Image.new("RGB", (w, h))
            im1 = ImageOps.mirror(im1.resize((x, h)))
            im2 = ImageOps.mirror(im2.resize((w - x, h)))
            temp.paste(im1, (0, 0))
            temp.paste(im2, (x, 0))
            temp = ImageOps.mirror(temp)
            out.append(temp)

    if way == 2:
        for y in range(1, h, h // 30):
            im1 = im2 = im.copy()
            temp = Image.new("RGB", (w, h))
            im1 = im1.resize((w, y))
            im2 = im2.resize((w, h - y))
            temp.paste(im1, (0, 0))
            temp.paste(im2, (0, y))
            out.append(temp)

    if way == 3:
        for y in range(1, h, h // 30):
            im1 = im2 = im.copy()
            temp = Image.new("RGB", (w, h))
            im1 = ImageOps.flip(im1.resize((w, y)))
            im2 = ImageOps.flip(im2.resize((w, h - y)))
            temp.paste(im1, (0, 0))
            temp.paste(im2, (0, y))
            temp = ImageOps.flip(temp)
            out.append(temp)

    output = io.BytesIO()
    output.name = "output.gif"
    out[0].save(output, save_all=True, append_images=out[1:], duration=1)
    output.seek(0)
    await reply.reply(file=output)
    await message.delete()


async def check_mediaa(message):
    reply = await message.get_reply_message()
    if not reply:
        return False
    if not reply.file:
        return False
    mime = reply.file.mime_type.split("/")[0].lower()
    if mime != "image":
        return False
    return reply


async def cropping(img):
    (x, y) = img.size
    cy = 5
    cx = 5
    sx = x // cx
    sy = y // cy
    if (sx * cx, sy * cy) != (x, y):
        img = img.resize((sx * cx, sy * cy))
    (lx, ly) = (0, 0)
    media = []
    for i in range(1, cy + 1):
        for o in range(1, cx + 1):
            mimg = img.crop((lx, ly, lx + sx, ly + sy))
            mimg = mimg.resize((512, 512))
            bio = io.BytesIO()
            bio.name = 'image.png'
            mimg.save(bio, 'PNG')
            media.append(bio.getvalue())
            lx = lx + sx
        lx = 0
        ly = ly + sy
    return media


async def parse(message):
    reply = await message.get_reply_message()
    if not reply:
        await message.edit("<b>Reply to Image!</b>")
        return None, None
    args = utils.get_args(message)
    pix = 100
    if args:
        args = args[0]
        if args.isdigit():
            pix = int(args) if int(args) > 0 else 100
    return reply, pix


async def dotify(message, reply, pix, mode):
    await message.edit("<b>Putting dots...</b>")
    count = 24
    im_ = Image.open(io.BytesIO(await reply.download_media(bytes)))
    if im_.mode == "RGBA":
        temp = Image.new("RGB", im_.size, "#000")
        temp.paste(im_, (0, 0), im_)
        im_ = temp

    im = im_.convert("L")
    im_ = im if mode else im_
    [_.thumbnail((pix, pix)) for _ in [im, im_]]
    w, h = im.size
    img = Image.new(im_.mode, (w * count + (count // 2), h * count + (count // 2)), 0)
    draw = ImageDraw.Draw(img)

    def cirsle(im, x, y, r, fill):
        x += r // 2
        y += r // 2
        draw = ImageDraw.Draw(im)
        draw.ellipse((x - r, y - r, x + r, y + r), fill)
        return im

    _x = _y = count // 2
    for x in range(w):
        for y in range(h):
            r = im.getpixel((x, y))
            fill = im_.getpixel((x, y))
            cirsle(img, _x, _y, r // count, fill)
            _y += count
        _x += count
        _y = count // 2

    out = io.BytesIO()
    out.name = "out.png"
    img.save(out)
    out.seek(0)
    await reply.reply(file=out)
    await message.delete()
async def get_img_from_msg(reply):
  if reply and reply.file:
      if not reply.file.mime_type == "image":
        return io.BytesIO(await reply.download_media(bytes))
      else:
        return None
  else:
      return None
async def invert_image(im, ext):
  image = Image.open(im)
  file = io.BytesIO()
  iswebp = True if ext == ".webp" else False
  file.name = "bw." + (".webp" if iswebp else ".png")
  if image.mode == 'RGBA':
      r,g,b,a = image.split()
      rgb_image = Image.merge('RGB', (r,g,b))
      inverted_image = PIL.ImageOps.invert(rgb_image)
      r2,g2,b2 = inverted_image.split()
      final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))
      if iswebp:
          final_transparent_image.thumbnail((512,512))
      final_transparent_image.save(file)
  else:
      inverted_image = PIL.ImageOps.invert(image)
      if iswebp:
          inverted_image.thumbnail((512,512))
      inverted_image.save(file)
  file.seek(0)
  return file
async def contrast(im, level, ext):
  image = ImageEnhance.Contrast(Image.open(im)).enhance(level)
  out = io.BytesIO()
  iswebp = True if ext == ".webp" else False
  if iswebp:
    image.thumbnail((512,512))
  out.name = "contrast." + (".webp" if iswebp else ".png")
  image.save(out)
  out.seek(0)
  return out
async def blwh(im, ext):
  image = Image.open(im).convert('L')
  out = io.BytesIO()
  iswebp = True if ext == ".webp" else False
  if iswebp:
    image.thumbnail((512,512))
  out.name = "bw." + (".webp" if iswebp else ".png")
  image.save(out)
  out.seek(0)
  return out
def setbright(im, level, ext):
    iswebp = True if ext == ".webp" else False
    image = ImageEnhance.Brightness(Image.open(im)).enhance(level)
    if iswebp:
        image.thumbnail((512,512))
    out = io.BytesIO()
    out.name = "brigth." + (".webp" if iswebp else ".png")
    image.save(out)
    out.seek(0)
    return out
def setsharpness(im, level, ext):
    iswebp = True if ext == ".webp" else False
    image = ImageEnhance.Sharpness(Image.open(im)).enhance(level)
    if iswebp:
        image.thumbnail((512,512))
    out = io.BytesIO()
    out.name = "sharpness." + (".webp" if iswebp else ".png")
    image.save(out)
    out.seek(0)
    return out