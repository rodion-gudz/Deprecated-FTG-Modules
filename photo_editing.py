import io, random, glob, os
from .. import loader, utils
from random import randint, uniform
from PIL import Image, ImageEnhance, ImageOps
from telethon.tl.types import DocumentAttributeFilename
import random
import logging


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
    strings = {"name": "Picture editing"}
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

    async def jpegcmd(self, message):
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
