import logging
from .. import loader, utils
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest, GetFullChatRequest
from telethon.tl.types import MessageActionChannelMigrateFrom, ChannelParticipantsAdmins, UserStatusOnline
from telethon.errors import (ChannelInvalidError, ChannelPrivateError, ChannelPublicGroupNaError)
from datetime import datetime
from telethon.tl.types import *
from telethon.tl.functions.messages import GetCommonChatsRequest
from telethon.tl.functions.users import GetFullUserRequest
from math import sqrt
logger = logging.getLogger(__name__)
from os import remove
from telethon import functions
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.errors.rpcerrorlist import MessageTooLongError
from telethon.errors import (UserIdInvalidError, UserNotMutualContactError, UserPrivacyRestrictedError, BotGroupsBlockedError, ChannelPrivateError, YouBlockedUserError,
                             UserBlockedError, ChatAdminRequiredError, UserKickedError, InputUserDeactivatedError, ChatWriteForbiddenError, UserAlreadyParticipantError)
from telethon.tl.types import (ChannelParticipantsAdmins, PeerChat, ChannelParticipantsBots)
from userbot import bot
import os
logger = logging.getLogger(__name__)
def register(cb):
    cb(TagAllMod())

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class TagAllMod(loader.Module):
    """Тэгает всех в чате."""
    strings = {"name": "Chat utils"}

    def __init__(self):
        self.config = loader.ModuleConfig("DEFAULT_MENTION_MESSAGE", "Hey", "Default message of mentions")
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client

    async def statacmd(self, m):
        await m.edit("<b>Считаем...</b>")
        al = str((await m.client.get_messages(m.to_id, limit=0)).total)
        ph = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterPhotos())).total)
        vi = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterVideo())).total)
        mu = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterMusic())).total)
        vo = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterVideo())).total)
        vv = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterRoundVideo())).total)
        do = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterDocument())).total)
        urls = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterUrl())).total)
        gifs = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterGif())).total)
        geos = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterGeo())).total)
        cont = str((await m.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterContacts())).total)
        await m.edit(
            ("<b>Всего сoообщений</b> {}\n" +
             "<b>Фоток:</b> {}\n" +
             "<b>Видосов:</b> {}\n" +
             "<b>Попсы:</b> {}\n" +
             "<b>Голосовых:</b> {}\n" +
             "<b>Кругляшков:</b> {}\n" +
             "<b>Файлов:</b> {}\n" +
             "<b>Ссылок:</b> {}\n" +
             "<b>Гифок:</b> {}\n" +
             "<b>Координат:</b> {}\n" +
             "<b>Контактов:</b> {}").format(al, ph, vi, mu, vo, vv, do, urls, gifs, geos, cont))

    async def tagallcmd(self, message):
        arg = utils.get_args_raw(message)
        logger.error(message)
        notifies = []
        async for user in self.client.iter_participants(message.to_id):
            notifies.append("<a href=\"tg://user?id="+ str(user.id) +"\">\u206c\u206f</a>")
        chunkss = list(chunks(notifies, 5))
        logger.error(chunkss)
        await message.delete()
        for chunk in chunkss:
            await self.client.send_message(message.to_id, (self.config["DEFAULT_MENTION_MESSAGE"] if not arg else arg) + '\u206c\u206f'.join(chunk))

    async def chatinfocmd(self, chatinfo):
        if chatinfo.chat:
            await chatinfo.edit("<b>Загрузка информации...</b>")
            chat = await get_chatinfo(chatinfo)
            caption = await fetch_info(chat, chatinfo)
            try:
                await chatinfo.client.send_message(chat.full_chat.id, str(caption),
                                                   file=await chatinfo.client.download_profile_photo(chat.full_chat.id,
                                                                                                     "chatphoto.jpg"))
            except Exception:
                await chatinfo.edit(f"<b>Произошла непредвиденная ошибка.</b>")
            await chatinfo.delete()
        else:
            await chatinfo.edit("<b>Это не чат!</b>")

    async def tagcmd(self, message):
        args = utils.get_args_raw(message).split(' ')
        tag = 'говно залупное\n                пашет.'
        try:
            user = await message.client.get_entity(args[0])
        except:
            return await message.edit('Пользователь не найден.')
        await message.delete()
        if len(args) == 1:
            tag = tag
        elif len(args) >= 2:
            tag = utils.get_args_raw(message).split(' ', 1)[1]
        await message.client.send_message(message.to_id, f'{tag} <a href="tg://user?id={user.id}">\u2060</a>')

    async def commoncmd(self, message):
        """Используй .common <@ или реплай>, чтобы узнать общие чаты с пользователем."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            return await message.edit('<b>Нет аргументов или реплая.</b>')
        await message.edit('<b>Считаем...</b>')
        try:
            if args:
                if args.isnumeric():
                    user = int(args)
                    user = await message.client.get_entity(user)
                else:
                    user = await message.client.get_entity(args)
            else:
                user = await utils.get_user(reply)
        except ValueError:
            return await message.edit('<b>Не удалось найти пользователя.</b>')
        msg = f'<b>Общие чаты с {user.first_name}:</b>\n'
        user = await message.client(GetFullUserRequest(user.id))
        comm = await message.client(GetCommonChatsRequest(user_id=user.user.id, max_id=0, limit=100))
        count = 0
        m = ''
        for chat in comm.chats:
            m += f'\n• <a href="tg://resolve?domain={chat.username}">{chat.title}</a> <b>|</b> <code>{chat.id}</code>'
            count += 1
        msg = f'<b>Общие чаты с {user.user.first_name}: {count}</b>\n'
        await message.edit(f'{msg} {m}')

    async def invitecmd(self, event):
        if event.fwd_from:
            return
        to_add_users = utils.get_args_raw(event)
        reply = await event.get_reply_message()
        if not to_add_users and not reply:
            await event.edit("<b>Нет аргументов.</b>")
        elif reply:
            to_add_users = str(reply.from_id)
        if to_add_users:
            if not event.is_group and not event.is_channel:
                return await event.edit("<b>Это не чат!</b>")
            else:
                if not event.is_channel and event.is_group:
                    # https://tl.telethon.dev/methods/messages/add_chat_user.html
                    for user_id in to_add_users.split(" "):
                        try:
                            userID = int(user_id)
                        except:
                            userID = user_id

                        try:
                            await event.client(functions.messages.AddChatUserRequest(chat_id=event.chat_id,
                                                                                     user_id=userID,
                                                                                     fwd_limit=1000000))
                        except ValueError:
                            await event.reply("<b>Неверный @ или ID.</b>")
                            return
                        except UserIdInvalidError:
                            await event.reply("<b>Неверный @ или ID.</b>")
                            return
                        except UserPrivacyRestrictedError:
                            await event.reply("<b>Настойки приватности пользователя не позволяют пригласить его.</b>")
                            return
                        except UserNotMutualContactError:
                            await event.reply("<b>Настойки приватности пользователя не позволяют пригласить его.</b>")
                            return
                        except ChatAdminRequiredError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except ChatWriteForbiddenError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except ChannelPrivateError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except UserKickedError:
                            await event.reply("<b>Пользователь кикнут из чата, обратитесь к администраторам.</b>")
                            return
                        except BotGroupsBlockedError:
                            await event.reply("<b>Бот заблокирован в чате, обратитесь к администраторам.</b>")
                            return
                        except UserBlockedError:
                            await event.reply("<b>Пользователь заблокирован в чате, обратитесь к администраторам.</b>")
                            return
                        except InputUserDeactivatedError:
                            await event.reply("<b>Аккаунт пользователя удалён.</b>")
                            return
                        except UserAlreadyParticipantError:
                            await event.reply("<b>Пользователь уже в группе.</b>")
                            return
                        except YouBlockedUserError:
                            await event.reply("<b>Вы заблокировали этого пользователя.</b>")
                            return
                    await event.edit("<b>Пользователь приглашён успешно!</b>")
                else:
                    # https://tl.telethon.dev/methods/channels/invite_to_channel.html
                    for user_id in to_add_users.split(" "):
                        try:
                            userID = int(user_id)
                        except:
                            userID = user_id

                        try:
                            await event.client(functions.channels.InviteToChannelRequest(channel=event.chat_id,
                                                                                         users=[userID]))
                        except ValueError:
                            await event.reply("<b>Неверный @ или ID.</b>")
                            return
                        except UserIdInvalidError:
                            await event.reply("<b>Неверный @ или ID.</b>")
                            return
                        except UserPrivacyRestrictedError:
                            await event.reply("<b>Настойки приватности пользователя не позволяют пригласить его.</b>")
                            return
                        except UserNotMutualContactError:
                            await event.reply("<b>Настойки приватности пользователя не позволяют пригласить его.</b>")
                            return
                        except ChatAdminRequiredError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except ChatWriteForbiddenError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except ChannelPrivateError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except UserKickedError:
                            await event.reply("<b>Пользователь кикнут из чата, обратитесь к администраторам.</b>")
                            return
                        except BotGroupsBlockedError:
                            await event.reply("<b>Бот заблокирован в чате, обратитесь к администраторам.</b>")
                            return
                        except UserBlockedError:
                            await event.reply("<b>Пользователь заблокирован в чате, обратитесь к администраторам.</b>")
                            return
                        except InputUserDeactivatedError:
                            await event.reply("<b>Аккаунт пользователя удалён.</b>")
                            return
                        except UserAlreadyParticipantError:
                            await event.reply("<b>Пользователь уже в группе.</b>")
                            return
                        except YouBlockedUserError:
                            await event.reply("<b>Вы заблокировали этого пользователя.</b>")
                            return
                        await event.edit("<b>Пользователь приглашён успешно!</b>")

    async def leavecmd(self, leave):
        reason = utils.get_args_raw(leave)
        try:
            if reason:
                await leave.edit(f"<b>До связи.\nПричина: {reason}.</b>")
            else:
                await leave.edit("<b>До связи.</b>")
            await leave.client(LeaveChannelRequest(leave.chat_id))
        except:
            await leave.edit("<b>Это не чат!</b>")
            return

    async def chatdumpcmd(self, message):
        num = False
        silent = False
        tome = False
        if (utils.get_args_raw(message)):
            a = utils.get_args_raw(message)
            if ("n" in a):
                num = True
            if ("s" in a):
                silent = True
            if ("m" in a):
                tome = True
        if silent == False:
            await message.edit("Dumping...")
        else:
            await message.delete()
        f = open(f"dump-{str(message.to_id)}.txt", "w")
        f.write("FNAME;LNAME;USER;ID;NUMBER\n")
        me = await message.client.get_me()
        for i in await message.client.get_participants(message.to_id):
            if (i.id == me.id): continue
            if (num):
                if (i.phone):
                    f.write(f"{str(i.first_name)};{str(i.last_name)};{str(i.username)};{str(i.id)};{str(i.phone)}\n")
            else:
                f.write(f"{str(i.first_name)};{str(i.last_name)};{str(i.username)};{str(i.id)};{str(i.phone)}\n")
        f.close()
        if tome:
            await message.client.send_file('me', f"dump-{str(message.to_id)}.txt",
                                           caption="Дамп чата " + str(message.to_id))
        else:
            await message.client.send_file(message.to_id, f"dump-{str(message.to_id)}.txt",
                                           caption="Дамп чата " + str(message.to_id))
        if silent == False:
            if tome:
                if num:
                    await message.edit("🖤Дамп юзеров чата сохранён в избранных!🖤")
                else:
                    await message.edit("🖤Дамп юзеров чата с открытыми номерами сохранён в избранных!🖤")
            else:
                await message.delete()

    async def userscmd(self, message):
        if message.chat:
            try:
                await message.edit("<b>Считаем...</b>")
                info = await message.client.get_entity(message.chat_id)
                title = info.title if info.title else "this chat"
                users = await message.client.get_participants(message.chat_id)
                mentions = f'<b>Пользователей в "{title}": {len(users)}</b> \n'
                if not utils.get_args_raw(message):
                    users = await bot.get_participants(message.chat_id)
                    for user in users:
                        if not user.deleted:
                            mentions += f"\n• <a href =\"tg://user?id={user.id}\">{user.first_name}</a> <b>|</b> <code>{user.id}</code>"
                        else:
                            mentions += f"\n• Удалённый аккаунт <b>|</b> <code>{user.id}</code>"
                else:
                    searchq = utils.get_args_raw(message)
                    users = await message.client.get_participants(message.chat_id, search=f"{searchq}")
                    mentions = f'<b>В чате "{title}" найдено {len(users)} пользователей с именем {searchq}:</b> \n'
                    for user in users:
                        if not user.deleted:
                            mentions += f"\n• <a href =\"tg://user?id={user.id}\">{user.first_name}</a> <b>|</b> <code>{user.id}</code>"
                        else:
                            mentions += f"\n• Удалённый аккаунт <b>|</b> <code>{user.id}</code>"
            except ChatAdminRequiredError as err:
                info = await message.client.get_entity(message.chat_id)
                title = info.title if info.title else "this chat"
                users = await message.client.get_participants(message.chat_id)
                mentions = f'<b>Пользователей в "{title}": {len(users)}</b> \n'
                mentions += " " + str(err) + "\n"
        else:
            await message.edit("<b>Это не чат!</b>")
            return
        try:
            await message.edit(mentions)
        except MessageTooLongError:
            await message.edit("<b>Черт, слишком большой чат. Загружаю список пользователей в файл...</b>")
            file = open("userslist.md", "w+")
            file.write(mentions)
            file.close()
            await message.client.send_file(message.chat_id,
                                           "userslist.md",
                                           caption="<b>Пользователей в {}:</b>".format(title),
                                           reply_to=message.id)
            remove("userslist.md")
            await message.delete()

    async def adminscmd(self, message):
        """Команда .admins показывает список всех админов в чате."""
        if message.chat:
            await message.edit("<b>Считаем...</b>")
            info = await message.client.get_entity(message.chat_id)
            title = info.title if info.title else "this chat"
            admins = await message.client.get_participants(message.chat_id, filter=ChannelParticipantsAdmins)
            mentions = f'<b>Админов в "{title}": {len(admins)}</b> \n'
            for user in await message.client.get_participants(message.chat_id, filter=ChannelParticipantsAdmins):
                if not user.deleted:
                    link = f"• <a href=\"tg://user?id={user.id}\">{user.first_name}</a>"
                    userid = f"<code>{user.id}</code>"
                    mentions += f"\n{link} <b>|</b> {userid}"
                else:
                    mentions += f"\n• Удалённый аккаунт <b>|</b> <code>{user.id}</code>"
            try:
                await message.edit(mentions, parse_mode="html")
            except MessageTooLongError:
                await message.edit("Черт, слишком много админов здесь. Загружаю список админов в файл...")
                file = open("adminlist.md", "w+")
                file.write(mentions)
                file.close()
                await message.client.send_file(message.chat_id,
                                               "adminlist.md",
                                               caption="<b>Админов в {}:<b>".format(title),
                                               reply_to=message.id)
                remove("adminlist.md")
                await message.delete()
        else:
            await message.edit("<b>Я слышал, что только чаты могут иметь админов...</b>")

    async def botscmd(self, message):
        """Команда .bots показывает список всех ботов в чате."""
        if message.chat:
            await message.edit("<b>Считаем...</b>")
            info = await message.client.get_entity(message.chat_id)
            title = info.title if info.title else "this chat"
            bots = await message.client.get_participants(message.to_id, filter=ChannelParticipantsBots)
            mentions = f'<b>Ботов в "{title}": {len(bots)}</b>\n'
            try:
                if isinstance(message.to_id, PeerChat):
                    await message.edit("<b>Я слышал, что только чаты могут иметь ботов...</b>")
                    return
                else:
                    async for user in message.client.iter_participants(message.chat_id, filter=ChannelParticipantsBots):
                        if not user.deleted:
                            link = f"• <a href=\"tg://user?id={user.id}\">{user.first_name}</a>"
                            userid = f"<code>{user.id}</code>"
                            mentions += f"\n{link} <b>|</b> {userid}"
                        else:
                            mentions += f"\n• Удалённый бот <b>|</b> <code>{user.id}</code>"
            except ChatAdminRequiredError as err:
                mentions += " " + str(err) + "\n"
            try:
                await message.edit(mentions, parse_mode="html")
            except MessageTooLongError:
                await message.edit(
                    "Черт, слишком много ботов здесь. Загружаю список ботов в файл...")
                file = open("botlist.md", "w+")
                file.write(mentions)
                file.close()
                await message.client.send_file(message.chat_id,
                                               "botlist.md",
                                               caption="<b>Ботов в {}:</b>".format(title),
                                               reply_to=message.id)
                remove("botlist.md")
                await message.delete()
        else:
            await message.edit("<b>Я слышал, что только чаты могут иметь ботов...</b>")
async def get_chatinfo(event):
    chat = utils.get_args_raw(event)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChannelRequest(chat))
    except:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await event.reply("<b>Недействительный канал/группа.</b>")
            return None
        except ChannelPrivateError:
            await event.reply("<b>Этот канал/группа приватная, либо я заблокирован там.</b>")
            return None
        except ChannelPublicGroupNaError:
            await event.reply("<b>Такой канал/группа не существует.</b>")
            return None
        except:
            chat = event.input_chat
            chat_info = await event.client(GetFullChannelRequest(chat))
            return chat_info
    return chat_info


async def fetch_info(chat, event):
    chat_obj_info = await event.client.get_entity(chat.full_chat.id)
    chat_title = chat_obj_info.title
    try:
        msg_info = await event.client(
            GetHistoryRequest(peer=chat_obj_info.id, offset_id=0, offset_date=datetime(2010, 1, 1),
                              add_offset=-1, limit=1, max_id=0, min_id=0, hash=0))
    except Exception:
        msg_info = None
        await event.edit("<b>Произошла непредвиденная ошибка.</b>")
    first_msg_valid = True if msg_info and msg_info.messages and msg_info.messages[0].id == 1 else False
    creator_valid = True if first_msg_valid and msg_info.users else False
    creator_id = msg_info.users[0].id if creator_valid else None
    creator_firstname = msg_info.users[0].first_name if creator_valid and msg_info.users[0].first_name is not None else "Удалённый аккаунт"
    creator_username = msg_info.users[0].username if creator_valid and msg_info.users[0].username is not None else None
    created = msg_info.messages[0].date if first_msg_valid else None
    former_title = msg_info.messages[0].action.title if first_msg_valid and type(msg_info.messages[0].action) is MessageActionChannelMigrateFrom and msg_info.messages[0].action.title != chat_title else None
    description = chat.full_chat.about
    members = chat.full_chat.participants_count if hasattr(chat.full_chat, "participants_count") else chat_obj_info.participants_count
    admins = chat.full_chat.admins_count if hasattr(chat.full_chat, "admins_count") else None
    banned_users = chat.full_chat.kicked_count if hasattr(chat.full_chat, "kicked_count") else None
    restrcited_users = chat.full_chat.banned_count if hasattr(chat.full_chat, "banned_count") else None
    users_online = 0
    async for i in event.client.iter_participants(event.chat_id):
        if isinstance(i.status, UserStatusOnline):
            users_online = users_online + 1
    group_stickers = chat.full_chat.stickerset.title if hasattr(chat.full_chat, "stickerset") and chat.full_chat.stickerset else None
    messages_viewable = msg_info.count if msg_info else None
    messages_sent = chat.full_chat.read_inbox_max_id if hasattr(chat.full_chat, "read_inbox_max_id") else None
    messages_sent_alt = chat.full_chat.read_outbox_max_id if hasattr(chat.full_chat, "read_outbox_max_id") else None
    username = chat_obj_info.username if hasattr(chat_obj_info, "username") else None
    bots_list = chat.full_chat.bot_info
    bots = 0
    slowmode = "Да" if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled else "Нет"
    slowmode_time = chat.full_chat.slowmode_seconds if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled else None
    restricted = "Да" if hasattr(chat_obj_info, "restricted") and chat_obj_info.restricted else "Нет"
    verified = "Да" if hasattr(chat_obj_info, "verified") and chat_obj_info.verified else "Нет"
    username = "@{}".format(username) if username else None
    creator_username = "@{}".format(creator_username) if creator_username else None

    if admins is None:
        try:
            participants_admins = await event.client(
                GetParticipantsRequest(channel=chat.full_chat.id, filter=ChannelParticipantsAdmins(),
                                       offset=0, limit=0, hash=0))
            admins = participants_admins.count if participants_admins else None
        except Exception:
            await event.edit("<b>Произошла непредвиденная ошибка.</b>")
    if bots_list:
        for bot in bots_list:
            bots += 1

    caption = "<b>ИНФОРМАЦИЯ О ЧАТЕ:</b>\n\n"
    caption += f"<b>ID:</b> {chat_obj_info.id}\n"
    if chat_title is not None:
        caption += f"<b>Название группы:</b> {chat_title}\n"
    if former_title is not None:
        caption += f"<b>Предыдущее название:</b> {former_title}\n"
    if username is not None:
        caption += f"<b>Тип группы:</b> Публичный\n"
        caption += f"<b>Линк:</b> {username}\n"
    else:
        caption += f"<b>Тип группы:</b> Приватный\n"
    if creator_username is not None:
        caption += f"<b>Создатель:</b> <code>{creator_username}</code>\n"
    elif creator_valid:
        caption += f"<b>Создатель:</b> <code><a href=\"tg://user?id={creator_id}\">{creator_firstname}</a></code>\n"
    if created is not None:
        caption += f"<b>Создан:</b> {created.date().strftime('%b %d, %Y')} - {created.time()}\n"
    else:
        caption += f"<b>Создан:</b> {chat_obj_info.date.date().strftime('%b %d, %Y')} - {chat_obj_info.date.time()}\n"
    if messages_viewable is not None:
        caption += f"<b>Видимые сообщения:</b> {messages_viewable}\n"
    if messages_sent:
        caption += f"<b>Всего сообщений:</b> {messages_sent}\n"
    elif messages_sent_alt:
        caption += f"<b>Всего сообщений:</b> {messages_sent_alt}\n"
    if members is not None:
        caption += f"<b>Участников:</b> {members}\n"
    if admins is not None:
        caption += f"<b>Админов:</b> {admins}\n"
    if bots_list:
        caption += f"<b>Ботов:</b> {bots}\n"
    if users_online:
        caption += f"<b>Сейчас онлайн:</b> {users_online}\n"
    if restrcited_users is not None:
        caption += f"<b>Ограниченных пользователей:</b> {restrcited_users}\n"
    if banned_users is not None:
        caption += f"<b>Забаненных пользователей:</b> {banned_users}\n"
    if group_stickers is not None:
        caption += f"<b>Стикеры группы:</b> <a href=\"t.me/addstickers/{chat.full_chat.stickerset.short_name}\">{group_stickers}</a>\n"
    caption += "\n"
    caption += f"<b>Слоумод:</b> {slowmode}"
    if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled:
        caption += f", {slowmode_time} секунд\n"
    else:
        caption += "\n"
    caption += f"<b>Ограничен:</b> {restricted}\n"
    if chat_obj_info.restricted:
        caption += f"> Платформа: {chat_obj_info.restriction_reason[0].platform}\n"
        caption += f"> Причина: {chat_obj_info.restriction_reason[0].reason}\n"
        caption += f"> Текст: {chat_obj_info.restriction_reason[0].text}\n\n"
    else:
        caption += ""
    if hasattr(chat_obj_info, "scam") and chat_obj_info.scam:
        caption += "<b>Скам</b>: да\n\n"
    if hasattr(chat_obj_info, "verified"):
        caption += f"<b>Верифицирован:</b> {verified}\n\n"
    if description:
        caption += f"<b>Описание:</b> \n\n<code>{description}</code>\n"
    return caption
