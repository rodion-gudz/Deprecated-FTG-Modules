from telethon import functions, types
from .. import loader, utils
from asyncio import sleep
import io
import os
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

def register(cb):
    cb(CuMod())


class CuMod(loader.Module):
    strings = {'name': 'User utils'}

    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.me = await client.get_me()

    async def copycmd(self, message):
        reply = await message.get_reply_message()
        user = None
        s = False
        a = False
        if utils.get_args_raw(message):
            args = utils.get_args_raw(message).split(" ")
            for i in args:
                if "s" == i.lower():
                    s = True
                elif "а" == i.lower() or "a" == i.lower():
                    a = True
                else:
                    try:
                        user = await message.client.get_entity(i)
                        break
                    except:
                        continue
        if user == None and reply != None: user = reply.sender
        if user == None and reply == None:
            if not s: await message.edit("Кого?")
            return
        if s: await message.delete()
        await message.delete()
        if a:
            avs = await message.client.get_profile_photos('me')
            if len(avs) > 0:
                await message.client(
                    functions.photos.DeletePhotosRequest(await message.client.get_profile_photos('me')))
        full = await message.client(GetFullUserRequest(user.id))
        if full.profile_photo:
            up = await message.client.upload_file(await message.client.download_profile_photo(user, bytes))
            await message.client(functions.photos.UploadProfilePhotoRequest(up))
        await message.client(UpdateProfileRequest(
            user.first_name if user.first_name != None else "",
            user.last_name if user.last_name != None else "",
            full.about[:70] if full.about != None else ""
        ))

    async def userinfocmd(self, whos):
        await whos.edit("<b>Получаю информацию о пользователе...</b>")
        replied_user = await get_user(whos)

        try:
            photo, caption = await fetch_info(replied_user, whos)
        except AttributeError:
            whos.edit("<b>Не могу найти информацию об этом пользователе.</b>")
            return

        message_id_to_reply = whos.reply_to_msg_id
        if not message_id_to_reply:
            message_id_to_reply = None

        try:
            await whos.client.send_file(whos.chat_id, photo, caption=caption,
                                        link_preview=False, force_document=False,
                                        reply_to=message_id_to_reply, parse_mode="html")
            if not photo.startswith("http"):
                os.remove(photo)
            await whos.delete()
        except TypeError:
            await whos.edit(caption, parse_mode="html")

async def get_user(event):
    """Получение информации о пользователе с реплая или аргумента."""
    if event.reply_to_msg_id and not utils.get_args_raw(event):
        previous_message = await event.get_reply_message()
        replied_user = await event.client(GetFullUserRequest(previous_message.from_id))
    else:
        user = utils.get_args_raw(event)
        if user.isnumeric():
            user = int(user)
        if not user:
            self_user = await event.client.get_me()
            user = self_user.id
        if event.entities is not None:
            probable_user_mention_entity = event.entities[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user
        try:
            user_object = await event.client.get_entity(user)
            replied_user = await event.client(GetFullUserRequest(user_object.id))
        except:
            self_user = await event.client.get_me()
            user = self_user.id
            user_object = await event.client.get_entity(user)
            replied_user = await event.client(GetFullUserRequest(user_object.id))
            return replied_user
    return replied_user


async def fetch_info(replied_user, event):
    """Подробная информация о пользователе."""
    replied_user_profile_photos = await event.client(GetUserPhotosRequest(user_id=replied_user.user.id,
                                                                          offset=42, max_id=0, limit=80))
    replied_user_profile_photos_count = "Пользователю нужна помощь с загрузкой аватарки."
    try:
        replied_user_profile_photos_count = replied_user_profile_photos.count
    except AttributeError as e:
        pass
    user_id = replied_user.user.id
    first_name = replied_user.user.first_name
    last_name = replied_user.user.last_name
    common_chat = replied_user.common_chats_count
    username = replied_user.user.username
    user_bio = replied_user.about
    is_bot = replied_user.user.bot
    if is_bot == False:
        is_bot = "Нет"
    else:
        is_bot = "Да"
    restricted = replied_user.user.restricted
    if restricted == False:
        restricted = "Нет"
    else:
        restricted = "Да"
    verified = replied_user.user.verified
    if verified == False:
        verified = "Нет"
    else:
        verified = "Да"
    photo = await event.client.download_profile_photo(user_id, str(user_id) + ".jpg", download_big=True)
    first_name = first_name.replace("\u2060", "") if first_name else "Пользователь не указал имя."
    last_name = last_name.replace("\u2060", "") if last_name else "Пользователь не указал фамилию."
    username = "@{}".format(username) if username else "У пользователя нет юзернейма."
    user_bio = "У пользователя нет информации о себе." if not user_bio else user_bio

    caption = "<b>ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:</b>\n\n"
    caption += f"<b>Имя:</b> {first_name}\n"
    caption += f"<b>Фамилия:</b> {last_name}\n"
    caption += f"<b>Юзернейм:</b> {username}\n"
    caption += f"<b>ID:</b> <code>{user_id}</code>\n"
    caption += f"<b>Бот:</b> {is_bot}\n"
    caption += f"<b>Ограничен:</b> {restricted}\n"
    caption += f"<b>Верифицирован:</b> {verified}\n\n"
    caption += f"<b>О себе:</b> \n<code>{user_bio}</code>\n\n"
    caption += f"<b>Кол-во аватарок в профиле:</b> {replied_user_profile_photos_count}\n"
    caption += f"<b>Общие чаты:</b> {common_chat}\n"
    caption += f"<b>Пермалинк:</b> "
    caption += f"<a href=\"tg://user?id={user_id}\">клик</a>"

    return photo, caption

