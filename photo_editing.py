import io, random, glob, os
from PIL import Image
from telethon.tl.types import DocumentAttributeFilename
from .. import loader, utils
from .. import loader, utils  # pylint: disable=relative-beyond-top-level
import io
from PIL import Image, ImageOps
from telethon.tl.types import DocumentAttributeFilename
import logging
import random
_C='png'
_B='name'
_A='image'
_R='отражает'
_P='часть.'
from ..  import loader as _L,utils as U
import logging,asyncio
from telethon.tl.types import DocumentAttributeFilename as DAF
from PIL import Image,ImageOps as IO
from io import BytesIO as ist

# Author: https://t.me/GovnoCodules

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
        except ValueError:
            await message.edit("ERROR INPUT=> ANGLE")

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
            B = A.photo;E = _C
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
