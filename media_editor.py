from pydub import effects
from telethon import types
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageOps, ImageFilter
import requests
import io
from telethon.tl.types import DocumentAttributeFilename
from moviepy.editor import VideoFileClip
import numpy as np
import math
import subprocess, os
import random
from .. import loader, utils


# Author: https://t.me/dekftgmodules and https://t.me/ftgmodulesbyfl1yd


class AudioEditorMod(loader.Module):
    """AudioEditor"""
    strings = {'name': 'Media editor',
               "reply": "Reply to video!",
               "error": "ERROR! TRY AGAIN!!",
               "processing": "DataDataMoshMosh!"
               }

    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.me = await client.get_me()

    async def basscmd(self, message):
        v = False
        accentuate_db = 2
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        if utils.get_args_raw(message):
            ar = utils.get_args_raw(message)
            try:
                int(ar)
                if int(ar) >= 2 and int(ar) <= 100:
                    accentuate_db = int(ar)
                else:
                    await message.edit("Укажите уровень BassBoost'а от 2 до 100!")
                    return
            except Exception as exx:
                await message.edit("Неверный аргумент!<br>" + str(exx))
                return
        else:
            accentuate_db = 2
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("BassBoost'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)

        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sample_track = list(audio.get_array_of_samples())
        est_mean = np.mean(sample_track)
        est_std = 3 * np.std(sample_track) / (math.sqrt(2))
        bass_factor = int(round((est_std - est_mean) * 0.005))
        attenuate_db = 0
        filtered = audio.low_pass_filter(bass_factor)
        out = (audio - attenuate_db).overlay(filtered + accentuate_db)
        m = io.BytesIO()

        if v:
            m.name = "voice.ogg"
            out.split_to_mono()
            await message.edit("Экспортируем...")
            out.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.edit("Отправляем...")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "BassBoosted.mp3"
            await message.edit("Экспортируем...")
            out.export(m, format="mp3")
            await message.edit("Отправляем...")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration,
                                             title=f"BassBoost {str(accentuate_db)}lvl", performer="BassBoost")])
        await message.delete()
        os.remove(fname)

    async def echoscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Echo'ярим...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            echo = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            echo = AudioSegment.from_file(fname)

        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        out = AudioSegment.empty()
        n = 200
        if os.path.isfile("none.mp3") == False:
            open("none.mp3", "wb").write(
                requests.get("https://raw.githubusercontent.com/Daniel3k00/files-for-modules/master/none.mp3").content)
        out += echo + AudioSegment.from_file("none.mp3")
        for i in range(5):
            echo = echo - 7
            out = out.overlay(echo, n)
            n += 200
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            out.split_to_mono()
            out.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Echo.mp3"
            out.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Эхо эффект",
                                             performer="Эхо эффект")])
        await message.delete()
        os.remove(fname)
        os.remove("none.mp3")

    async def volupcmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Vol'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname).apply_gain(+10)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname).apply_gain(+10)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "VolUp.mp3"
            audio.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="VolUp",
                                             performer="VolUp")])
        await message.delete()
        os.remove(fname)

    async def voldwcmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Vol'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname).apply_gain(-10)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname).apply_gain(-10)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "VolDown.mp3"
            audio.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="VolDown",
                                             performer="VolDown")])
        await message.delete()
        os.remove(fname)

    async def revscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Reverse'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        rev = audio.reverse()
        audio = rev
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Reversed.mp3"
            audio.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Reversed",
                                             performer="Reversed")])
        await message.delete()
        os.remove(fname)

    async def repscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Repeat'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        audio = audio * 2
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Repeated.mp3"
            audio.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Repeated",
                                             performer="Repeated")])
        await message.delete()
        os.remove(fname)

    async def slowscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Замедляем...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * 0.5)
        })
        sound = sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Slow.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Slowed",
                                             performer="Slowed")])
        await message.delete()

    async def fastscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Ускоряем...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * 1.5)
        })
        sound = sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Fast.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id)
        await message.delete()

    async def leftscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Pan'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            sound = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            sound = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound = effects.pan(sound, -1.0)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Left.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Fasted",
                                             performer="Fasted")])
        await message.delete()

    async def rightscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Pan'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            sound = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            sound = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound = effects.pan(sound, +1.0)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Right.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Right",
                                             performer="Right")])
        await message.delete()

    async def normscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Нормализуем звук...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound = effects.normalize(sound)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Normalized.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Left",
                                             performer="Left")])
        await message.delete()

    async def byrobertscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Делаем магию...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        if os.path.isfile("directed.mp3") == False:
            open("directed.mp3", "wb").write(requests.get(
                "https://raw.githubusercontent.com/Daniel3k00/files-for-modules/master/directed.mp3").content)
        audio.export("temp.mp3", format="mp3")
        os.remove(fname)
        out = AudioSegment.empty()
        out += AudioSegment.from_file("temp.mp3")
        out += AudioSegment.from_file("directed.mp3").apply_gain(+10)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            out.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "DirectedAudio.mp3"
            out.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Directed",
                                             performer="Robert B. Weide")])
        await message.delete()
        os.remove("temp.mp3")
        os.remove("directed.mp3")

    async def cutcmd(self, event):
        """Используй .cut <начало(сек):конец(сек)> <реплай на аудио/видео/гиф>."""
        args = utils.get_args_raw(event).split(':')
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            return await event.edit('Reply to media')
        if reply.media:
            if args:
                if len(args) == 2:
                    try:
                        await event.edit('Downloading...')
                        smth = reply.file.ext
                        await event.client.download_media(reply.media, f'uncutted{smth}')
                        await event.edit('Cutting...')
                        os.system(f'ffmpeg -i uncutted{smth} -ss {args[0]} -to {args[1]} -c copy cutted{smth} -y')
                        await event.edit('Sending...')
                        await event.client.send_file(event.to_id, f'cutted{smth}', reply_to=reply.id)
                        os.system('rm -rf uncutted* cutted*')
                        await event.delete()
                    except:
                        await event.edit('Reply to media')
                        os.system('rm -rf uncutted* cutted*')
                        return
                else:
                    return await event.edit('No arguments')
            else:
                return await event.edit('No arguments')

    async def roundcmd(self, message):
        """.round <Reply to image/sticker or video/gif>"""
        reply = None
        if message.is_reply:
            reply = await message.get_reply_message()
            data = await check_media(reply)
            if isinstance(data, bool):
                await utils.answer(message, "<b>Reply to image/sticker or video/gif!</b>")
                return
        else:
            await utils.answer(message, "<b>Reply to image/sticker or video/gif!</b>")
            return
        data, type = data
        if type == "img":
            await message.edit("<b>Processing image</b>📷")
            img = io.BytesIO()
            bytes = await message.client.download_file(data, img)
            im = Image.open(img)
            w, h = im.size
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            img.paste(im, (0, 0))
            m = min(w, h)
            img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
            w, h = img.size
            mask = Image.new('L', (w, h), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((10, 10, w - 10, h - 10), fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(2))
            img = ImageOps.fit(img, (w, h))
            img.putalpha(mask)
            im = io.BytesIO()
            im.name = "img.webp"
            img.save(im)
            im.seek(0)
            await message.client.send_file(message.to_id, im, reply_to=reply)
        else:
            await message.edit("<b>Processing video</b>🎥")
            await message.client.download_file(data, "video.mp4")
            video = VideoFileClip("video.mp4")
            video.reader.close()
            w, h = video.size
            m = min(w, h)
            box = [(w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2]
            video = video.crop(*box)
            await message.edit("<b>Saving video</b>📼")
            video.write_videofile("result.mp4")
            await message.client.send_file(message.to_id, "result.mp4", video_note=True, reply_to=reply)
            os.remove("video.mp4")
            os.remove("result.mp4")
        await message.delete()

    async def datamoshcmd(self, message):
        fn = "if_you_see_it_then_delete_it"
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("".join([random.choice(html).format(ch) for ch in self.strings("reply", message)]))
            return
        if not reply.video:
            await message.edit("".join([random.choice(html).format(ch) for ch in self.strings("reply", message)]))
            return
        else:
            await reply.download_media(fn + "1.mp4")

        lvl = 1
        fp = False
        args = utils.get_args(message)
        if args:
            if len(args) == 1:
                if args[0].isdigit():
                    lvl = int(args[0])
                    if lvl <= 0:
                        lvl = 1
                else:
                    fp = True
            if len(args) > 1:
                fp = True
                if args[0].isdigit():
                    lvl = int(args[0])
                    if lvl <= 0:
                        lvl = 1
                elif args[1].isdigit():
                    fp = True
                    lvl = int(args[1])
                    if lvl <= 0:
                        lvl = 1

        await message.edit("".join([random.choice(html).format(ch) for ch in self.strings("processing", message)]))
        subprocess.call(f'ffmpeg -loglevel quiet -y -i {fn}1.mp4 -crf 0 -bf 0 {fn}1.avi', shell=True)
        try:
            _f = open(fn + '1.avi', 'rb')
            f_ = open(fn + '2.avi', 'wb')
        except FileNotFoundError:
            await message.edit("".join([random.choice(html).format(ch) for ch in self.strings("error", message)]))
            os.system(f"rm -f {fn}*")
            return

        frs = _f.read().split(b'00dc')
        fi = b'\x00\x01\xb0'
        cf = 0
        for _, fr in enumerate(frs):
            if fp == False:
                f_.write(fr + b'00dc')
                cf += 1
                if fr[5:8] == fi:
                    fp = True
            else:
                if fr[5:8] != fi:
                    cf += 1
                    for i in range(lvl):
                        f_.write(fr + b'00dc')
        f_.close()
        _f.close()

        subprocess.call(f'ffmpeg -loglevel quiet -y -i {fn}2.avi {fn}2.mp4', shell=True)
        await reply.reply(file=fn + "2.mp4")
        os.system(f"rm -f {fn}*")
        await message.delete()

    async def fvcmd(self, message):
        reply = await message.get_reply_message()
        lvl = 0
        if not reply:
            await message.edit("Reply to media")
            return
        if utils.get_args_raw(message):
            ar = utils.get_args_raw(message)
            try:
                int(ar)
                if int(ar) >= 10 and int(ar) <= 100:
                    lvl = int(ar)
                else:
                    await message.edit("No Argument")
                    return
            except Exception as exx:
                await message.edit("No Argument" + str(exx))
                return
        else:
            lvl = 100
        await message.edit("<b>Distorting...</b>")
        sa = False
        m = io.BytesIO()
        fname = await message.client.download_media(message=reply.media)
        if (fname.endswith(".oga") or fname.endswith(".ogg")):
            audio = AudioSegment.from_file(fname, "ogg")
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".3gp") or fname.endswith(
                ".mpeg") or fname.endswith(".wav"):
            sa = True
            audio = AudioSegment.from_file(fname, "mp3")
        else:
            await message.edit("No file</b>")
            os.remove(fname)
            return
        audio = audio + lvl
        if (sa):
            m.name = "Distorted.mp3"
            audio.export(m, format="mp3")
        else:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", codec="libopus", bitrate="64k")
        m.seek(0)
        if (sa):
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title=f"Distorted",
                                             performer="Distort")])
        else:
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        await message.delete()
        os.remove(fname)


html = ["<b>{}<b>", "<code>{}</code>", "<i>{}</i>", "<del>{}</del>", "<u>{}</u>",
        '<a href="https://bruh.moment">{}</a>']


async def check_media(reply):
    type = "img"
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply.media.document.attributes:
                return False
            if reply.gif or reply.video:
                type = "vid"
            if reply.audio or reply.voice:
                return False
            data = reply.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return (data, type)
