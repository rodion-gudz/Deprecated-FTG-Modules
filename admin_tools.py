# Admin Tools for Friendly-Telegram UserBot.
# Copyright (C) 2020 @Fl1yd, @AtiksX.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ======================================================================

import io, time
import logging

from .. import loader, utils, security
from PIL import Image
import telethon
from telethon.errors import (ChatAdminRequiredError, UserAdminInvalidError, FloodWaitError, PhotoCropSizeSmallError)
from telethon.tl.types import (ChatAdminRights, ChatBannedRights)
from telethon.tl.functions.channels import (EditAdminRequest, EditBannedRequest, EditPhotoRequest,
                                            DeleteUserHistoryRequest)
from telethon.tl.functions.messages import EditChatAdminRequest
from userbot import bot
from telethon import events

# ================== КОНСТАНТЫ ========================

PROMOTE_RIGHTS = ChatAdminRights(add_admins=False,
                                 invite_users=True,
                                 change_info=False,
                                 ban_users=True,
                                 delete_messages=True,
                                 pin_messages=True)

DEMOTE_RIGHTS = ChatAdminRights(post_messages=None,
                                add_admins=None,
                                invite_users=None,
                                change_info=None,
                                ban_users=None,
                                delete_messages=None,
                                pin_messages=None,
                                edit_messages=None)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=None,
                                 send_messages=False,
                                 send_media=False,
                                 send_stickers=False,
                                 send_gifs=False,
                                 send_games=False,
                                 send_inline=False,
                                 embed_links=False)

BANNED_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=True,
                                 send_messages=True,
                                 send_media=True,
                                 send_stickers=True,
                                 send_gifs=True,
                                 send_games=True,
                                 send_inline=True,
                                 embed_links=True)

UNBAN_RIGHTS = ChatBannedRights(until_date=None,
                                view_messages=None,
                                send_messages=None,
                                send_media=None,
                                send_stickers=None,
                                send_gifs=None,
                                send_games=None,
                                send_inline=None,
                                embed_links=None)


# =====================================================

def register(cb):
    cb(AdminToolsMod())


logger = logging.getLogger(__name__)


class AdminToolsMod(loader.Module):
    """Администрирование чата"""
    strings = {'name': 'Admin Tools',
               'no_reply': '<b>Нет реплая на картинку/стикер.</b>',
               'not_pic': '<b>Это не картинка/стикер</b>',
               'wait': '<b>Минуточку...</b>',
               'pic_so_small': '<b>Картинка слишком маленькая, попробуйте другую.</b>',
               'pic_changed': '<b>Картинка чата изменена.</b>',
               'promote_none': '<b>Некого повышать.</b>',
               'who': '<b>Кто это?</b>',
               'not_admin': '<b>Я здесь не админ.</b>',
               'promoted': '<b>{} повышен в правах администратора.\nРанг: {}</b>',
               'wtf_is_it': '<b>Что это?</b>',
               'this_isn`t_a_chat': '<b>Это не чат!</b>',
               'demote_none': '<b>Некого понижать.</b>',
               'demoted': '<b>{} понижен в правах администратора.</b>',
               'pinning': '<b>Пин...</b>',
               'pin_none': '<b>Ответь на сообщение чтобы закрепить его.</b>',
               'unpinning': '<b>Анпин...</b>',
               'unpin_none': '<b>Нечего откреплять.</b>',
               'no_rights': '<b>У меня нет прав.</b>',
               'pinned': '<b>Закреплено успешно!</b>',
               'unpinned': '<b>Откреплено успешно!</b>',
               'can`t_kick': '<b>Не могу кикнуть пользователя.</b>',
               'kicking': '<b>Кик...</b>',
               'kick_none': '<b>Некого кикать.</b>',
               'kicked': '<b>{} кикнут из чата.</b>',
               'kicked_for_reason': '<b>{} кикнут из чата.\nПричина: {}.</b>',
               'banning': '<b>Бан...</b>',
               'banned': '<b>{} забанен в чате.</b>',
               'banned_for_reason': '<b>{} забанен в чате.\nПричина: {}</b>',
               'ban_none': '<b>Некому давать бан.</b>',
               'unban_none': '<b>Некого разбанить.</b>',
               'unbanned': '<b>{} разбанен в чате.</b>',
               'mute_none': '<b>Некому давать мут.</b>',
               'muted': '<b>{} теперь в муте на </b>',
               'no_args': '<b>Неверно указаны аргументы.</b>',
               'unmute_none': '<b>Некого размутить.</b>',
               'unmuted': '<b>{} теперь не в муте.</b>',
               'no_reply': '<b>Нет реплая.</b>',
               'deleting': '<b>Удаление...</b>',
               'no_args_or_reply': '<b>Нет аргументов или реплая.</b>',
               'deleted': '<b>Все сообщения от {} удалены.</b>',
               'del_u_search': '<b>Поиск удалённых аккаунтов...</b>',
               'del_u_kicking': '<b>Кик удалённых аккаунтов...\nОх~, я могу это сделать?!</b>'}

    async def ecpcmd(self, message):
        """Команда .ecp изменяет картинку чата.\nИспользование: .ecp <реплай на картинку/стикер>."""
        if message.chat:
            try:
                reply = await message.get_reply_message()
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                if reply:
                    pic = await check_media(message, reply)
                    if not pic:
                        return await utils.answer(message, self.strings('not_pic', message))
                else:
                    return await utils.answer(message, self.strings('no_reply', message))
                await utils.answer(message, self.strings('wait', message))
                what = resizepic(pic)
                if what:
                    try:
                        await message.client(EditPhotoRequest(message.chat_id, await message.client.upload_file(what)))
                    except PhotoCropSizeSmallError:
                        return await utils.answer(message, self.strings('pic_so_small', message))
                await utils.answer(message, self.strings('pic_changed', message))
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def promotecmd(self, message):
        """Команда .promote повышает пользователя в правах администратора.\nИспользование: .promote <@ или реплай> <ранг>."""
        if message.chat:
            try:
                args = utils.get_args_raw(message).split(' ')
                reply = await message.get_reply_message()
                rank = 'одмэн'
                chat = await message.get_chat()
                adm_rights = chat.admin_rights
                if not adm_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                if reply:
                    args = utils.get_args_raw(message)
                    if args:
                        rank = args
                    else:
                        rank = rank
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if len(args) == 1:
                        rank = rank
                    elif len(args) >= 2:
                        rank = utils.get_args_raw(message).split(' ', 1)[1]
                try:
                    await message.client(EditAdminRequest(message.chat_id, user.id, ChatAdminRights(add_admins=False,
                                                                                                    invite_users=adm_rights.invite_users,
                                                                                                    change_info=False,
                                                                                                    ban_users=adm_rights.ban_users,
                                                                                                    delete_messages=adm_rights.delete_messages,
                                                                                                    pin_messages=adm_rights.pin_messages),
                                                          rank))
                except ChatAdminRequiredError:
                    return await utils.answer(message, self.strings('no_rights', message))
                else:
                    return await utils.answer(message, self.strings('promoted', message).format(user.first_name, rank))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def demotecmd(self, message):
        """Команда .demote понижает пользователя в правах администратора.\nИспользование: .demote <@ или реплай>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('demote_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                try:
                    if message.is_channel:
                        await message.client(EditAdminRequest(message.chat_id, user.id, DEMOTE_RIGHTS, ""))
                    else:
                        await message.client(EditChatAdminRequest(message.chat_id, user.id, False))
                except ChatAdminRequiredError:
                    return await utils.answer(message, self.strings('no_rights', message))
                else:
                    return await utils.answer(message, self.strings('demoted', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args'))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def pincmd(self, message):
        """Команда .pin закрепляет сообщение в чате.\nИспользование: .pin <реплай>."""
        if not message.is_private:
            reply = await message.get_reply_message()
            if not reply:
                return await utils.answer(message, self.strings('pin_none', message))
            await utils.answer(message, self.strings('pinning', message))
            try:
                await message.client.pin_message(message.chat, message=reply.id, notify=False)
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
            await utils.answer(message, self.strings('pinned', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def unpincmd(self, message):
        """Команда .unpin открепляет закрепленное сообщение в чате.\nИспользование: .unpin."""
        if not message.is_private:
            await utils.answer(message, self.strings('unpinning', message))
            try:
                await message.client.pin_message(message.chat, message=None, notify=None)
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
            await utils.answer(message, self.strings('unpinned', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def purgecmd(self, message):
        """Purge from the replied message"""
        if not message.is_reply:
            await utils.answer(message, self.strings("from_where", message))
            return

        from_users = set()
        args = utils.get_args(message)
        for arg in args:
            try:
                entity = await message.client.get_entity(arg)
                if isinstance(entity, telethon.tl.types.User):
                    from_users.add(entity.id)
            except ValueError:
                pass

        msgs = []
        from_ids = set()
        if await message.client.is_bot():
            if not message.is_channel:
                await utils.answer(message, self.strings("not_supergroup_bot", message))
                return
            for msg in range(message.reply_to_msg_id, message.id + 1):
                msgs.append(msg)
                if len(msgs) >= 99:
                    logger.debug(msgs)
                    await message.client.delete_messages(message.to_id, msgs)
                    msgs.clear()
        else:
            async for msg in message.client.iter_messages(
                    entity=message.to_id,
                    min_id=message.reply_to_msg_id - 1,
                    reverse=True):
                if from_users and msg.from_id not in from_users:
                    continue
                msgs.append(msg.id)
                from_ids.add(msg.from_id)
                if len(msgs) >= 99:
                    logger.debug(msgs)
                    await message.client.delete_messages(message.to_id, msgs)
                    msgs.clear()
        if msgs:
            logger.debug(msgs)
            await message.client.delete_messages(message.to_id, msgs)
        await self.allmodules.log("purge", group=message.to_id, affected_uids=from_ids)

    async def welcomecmd(self, message):
        """Включить/выключить приветствие новых пользователей в чате. Используй: .welcome."""
        welcome = self.db.get("Welcome", "welcome", {})
        chatid = str(message.chat_id)
        if chatid not in welcome:
            welcome.setdefault(chatid, {})
        if "message" not in welcome[chatid]:
            welcome[chatid].setdefault("message", "Добро пожаловать в чат!")
        if "status" not in welcome[chatid]:
            welcome[chatid].setdefault("status", False)

        if welcome[chatid]["status"] == False or welcome[chatid]["status"] == None:
            welcome[chatid]["status"] = True
            self.db.set("Welcome", "welcome", welcome)
            return await message.edit("<b>[Welcome Mode]</b> Активирован!")
        else:
            welcome.pop(chatid)
            self.db.set("Welcome", "welcome", welcome)
            return await message.edit("<b>[Welcome Mode]</b> Деактивирован!")

    async def setwelcomecmd(self, message):
        """Установить новое приветствие новых пользователей в чате.\nИспользуй: .setwelcome <текст (можно использовать {name}; {chat})>; ничего."""
        welcome = self.db.get("Welcome", "welcome", {})
        args = utils.get_args_raw(message)
        chatid = str(message.chat_id)
        chat = await message.client.get_entity(int(chatid))
        if not args:
            try:
                return await message.edit(f'<b>Приветствие новых пользователей в "{chat.title}":</b>\n\n'
                                          f'<b>Статус:</b> Включено.\n'
                                          f'<b>Приветствие:</b> {welcome[chatid]["message"]}\n\n'
                                          f'<b>~ Установить новое приветствие можно с помощью команды:</b> .setwelcome <текст>.')

            except KeyError:
                return await message.edit(f'<b>Приветствие новых пользователей в "{chat.title}":</b>\n\n'
                                          f'<b>Статус:</b> Отключено.')
        else:
            try:
                welcome[chatid]["message"] = args
                self.db.set("Welcome", "welcome", welcome)
                return await message.edit("<b>Новое приветствие установлено успешно!</b>")
            except KeyError:
                return await message.edit(f'<b>Приветствие новых пользователей в "{chat.title}":</b>\n\n'
                                          f'<b>Статус:</b> Отключено')

    @bot.on(events.ChatAction)
    async def watcher(self, event):
        """Интересно, почему он именно watcher называется... 🤔"""
        try:
            welcome = self.db.get("Welcome", "welcome", {})
            user = await event.get_user()
            chat = await event.get_chat()
            chatid = str(event.chat_id)
            if chatid in welcome:
                if event.user_joined or event.user_added:
                    await event.reply((welcome[chatid]["message"]).format(name=user.first_name, chat=chat.title))
        except (AttributeError, TypeError):
            pass

    @loader.group_admin_delete_messages
    @loader.ratelimit
    async def delcmd(self, message):
        msgs = [message.id]
        if not message.is_reply:
            if await message.client.is_bot():
                await utils.answer(message, self.strings("delete_what", message))
                return
            msg = await message.client.iter_messages(message.to_id, 1, max_id=message.id).__anext__()
        else:
            msg = await message.get_reply_message()
        msgs.append(msg.id)
        logger.debug(msgs)
        await message.client.delete_messages(message.to_id, msgs)
        await self.allmodules.log("delete", group=message.to_id, affected_uids=[msg.from_id])

    async def addbwcmd(self, message):
        """Добавить слово в список "Плохих слов". Используй: .addbw <слово>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не админ здесь.</b>")
            else:
                if chat.admin_rights.delete_messages == False:
                    return await message.edit("<b>У меня нет нужных прав.</b>")
        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message)
        if not args: return await message.edit("<b>[BanWords]</b> Нет аргументов.")
        chatid = str(message.chat_id)
        if chatid not in words:
            words.setdefault(chatid, [])
        if "stats" not in words:
            words.setdefault("stats", {})
        if chatid not in words["stats"]:
            words["stats"].setdefault(chatid, {})
        if args not in words[chatid]:
            if ", " in args:
                args = args.split(', ')
                words[chatid].extend(args)
                self.db.set("BanWords", "bws", words)
                await message.edit(
                    f"<b>[BanWords]</b> В список чата добавлены слова - \"<code>{'; '.join(args)}</code>\".")
            else:
                words[chatid].append(args)
                self.db.set("BanWords", "bws", words)
                await message.edit(f"<b>[BanWords]</b> В список чата добавлено слово - \"<code>{args}</code>\".")
        else:
            return await message.edit("<b>[BanWords]</b> Такое слово уже есть в списке слов чата.")

    async def rmbwcmd(self, message):
        """Удалить слово из список "Плохих слов". Используй: .rmbw <слово или all/clearall (по желанию)>."""
        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message)
        if not args: return await message.edit("<b>[BanWords]</b> Нет аргументов.")
        chatid = str(message.chat_id)
        try:
            if args == "all":
                words.pop(chatid)
                words["stats"].pop(chatid)
                self.db.set("BanWords", "bws", words)
                return await message.edit("<b>[BanWords]</b> Из списка чата удалены все слова.")
            if args == "clearall":
                self.db.set("BanWords", "bws", {})
                return await message.edit("<b>[BanWords]</b> Все списки из всех чатов были удалены.")
            words[chatid].remove(args)
            if len(words[chatid]) == 0:
                words.pop(chatid)
            self.db.set("BanWords", "bws", words)
            await message.edit(f"<b>[BanWords]</b> Из списка чата удалено слово - \"<code>{args}</code>\".")
        except KeyError:
            return await message.edit("<b>Этого слова нет в словаре этого чата.</b>")

    async def bwscmd(self, message):
        """Посмотреть список "Плохих слов". Используй: .bws."""
        words = self.db.get("BanWords", "bws", {})
        chatid = str(message.chat_id)
        try:
            ls = words[chatid]
        except KeyError:
            return await message.edit("<b>[BanWords]</b> В этом чате нет списка слов.")
        word = ""
        for _ in ls:
            word += f"• <code>{_}</code>\n"
        await message.edit(f"<b>[BanWords]</b> Список слов в этом чате:\n\n{word}")

    async def bwstatscmd(self, message):
        """Статистика "Плохих слов". Используй: .bwstats <clear (по желанию)>."""
        words = self.db.get("BanWords", "bws", {})
        chatid = str(message.chat_id)
        args = utils.get_args_raw(message)
        if args == "clear":
            words["stats"].pop(chatid)
            self.db.set("BanWords", "bws", words)
            return await message.edit("<b>[BanWords]</b> Статистика пользователей чата сброшена.")
        w = ""
        try:
            for _ in words["stats"][chatid]:
                if _ != "kick" and words["stats"][chatid][_] != 0:
                    user = await message.client.get_entity(int(_))
                    w += f'• <a href="tg://user?id={int(_)}">{user.first_name}</a>: <code>{words["stats"][chatid][_]}</code>\n'
            return await message.edit(f"<b>[BanWords]</b> Кто использовал спец.слова:\n\n{w}")
        except KeyError:
            return await message.edit("<b>[BanWords]</b> В этом чате нет тех, кто использовал спец.слова.")

    async def swbwcmd(self, message):
        """Переключить режим "Плохих слов". Используй: .swbw"""
        words = self.db.get("BanWords", "bws", [])
        args = utils.get_args_raw(message)
        chatid = str(message.chat_id)

        if chatid not in words:
            words.setdefault(chatid, [])
        if "stats" not in words:
            words.setdefault("stats", {})
        if chatid not in words["stats"]:
            words["stats"].setdefault(chatid, {})
        if "kick" not in words["stats"][chatid]:
            words["stats"][chatid].setdefault("kick", None)

        if words["stats"][chatid]["kick"] == False or words["stats"][chatid]["kick"] == None:
            words["stats"][chatid]["kick"] = True
            self.db.set("BanWords", "bws", words)
            return await message.edit("<b>[BanWords]</b> Режим кик участников включен.\nЛимит: 5 спец.слова.")

        elif words["stats"][chatid]["kick"] == True:
            words["stats"][chatid]["kick"] = False
            self.db.set("BanWords", "bws", words)
            return await message.edit(f"<b>[BanWords]</b> Режим кик участников выключен.")

    async def watcher(self, message):
        """мда"""
        if message.sender_id == (await message.client.get_me()).id: return
        words = self.db.get("BanWords", "bws", [])
        chatid = str(message.chat_id)
        userid = str(message.sender_id)
        user = await message.client.get_entity(int(userid))
        if chatid not in str(words): return
        if userid not in words["stats"][chatid]:
            words["stats"][chatid].setdefault(userid, 0)
        ls = words[chatid]
        for _ in ls:
            if _ in message.text.lower().split():
                count = words["stats"][chatid][userid]
                words["stats"][chatid].update({userid: count + 1})
                self.db.set("BanWords", "bws", words)
                if "kick" in words["stats"][chatid]:
                    if words["stats"][chatid]["kick"] == True:
                        if count == 5:
                            await message.client.kick_participant(int(chatid), int(userid))
                            words["stats"][chatid].pop(userid)
                            self.db.set("BanWords", "bws", words)
                            await message.respond(
                                f"<b>[BanWords]</b> {user.first_name} достиг лимит (5) спец.слова, и был кикнут из чата.")
                await message.client.delete_messages(message.chat_id, message.id)

    async def kickcmd(self, message):
        """Команда .kick кикает пользователя.\nИспользование: .kick <@ или реплай>."""
        if not message.is_private:
            try:
                args = utils.get_args_raw(message).split(' ')
                reason = utils.get_args_raw(message)
                reply = await message.get_reply_message()
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        reason = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(message).split(' ', 1)[1]
                await utils.answer(message, self.strings('kicking', message))
                try:
                    await message.client.kick_participant(message.chat_id, user.id)
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
                if reason == False:
                    return await utils.answer(message, self.strings('kicked', message).format(user.first_name))
                if reason:
                    return await utils.answer(message,
                                              self.strings('kicked_for_reason', message).format(user.first_name,
                                                                                                reason))
                return await utils.answer(message, self.strings('kicked', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def bancmd(self, message):
        """Команда .ban даёт бан пользователю.\nИспользование: .ban <@ или реплай>."""
        if not message.is_private:
            try:
                args = utils.get_args_raw(message).split(' ')
                reason = utils.get_args_raw(message)
                reply = await message.get_reply_message()
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        reason = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(message).split(' ', 1)[1]
                try:
                    await utils.answer(message, self.strings('banning', message))
                    await message.client(EditBannedRequest(message.chat_id, user.id,
                                                           ChatBannedRights(until_date=None, view_messages=True)))
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
                if reason == False:
                    return await utils.answer(message, self.strings('banned', message).format(user.first_name))
                if reason:
                    return await utils.answer(message,
                                              self.strings('banned_for_reason', message).format(user.first_name,
                                                                                                reason))
                return await utils.answer(message, self.strings('banned', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def unbancmd(self, message):
        """Команда .unban для разбана пользователя.\nИспользование: .unban <@ или реплай>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args(message)
                    if not args:
                        return await utils.answer(message, self.strings('unban_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                await message.client(
                    EditBannedRequest(message.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=False)))
                return await utils.answer(message, self.strings('unbanned', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def mutecmd(self, message):
        """Команда .mute даёт мут пользователю.\nИспользование: .mute <@ или реплай> <время (1m, 1h, 1d)>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    who = utils.get_args_raw(message).split(' ')
                    user = await message.client.get_entity(who[0] if not who[0].isnumeric() else int(who[0]))

                    if len(who) == 1:
                        timee = ChatBannedRights(until_date=True, send_messages=True)
                        await message.client(EditBannedRequest(message.chat_id, user.id, timee))
                        await message.edit('<b>{} теперь в муте.</b>'.format(user.first_name))
                        return

                    if not user:
                        return await utils.answer(message, self.strings('mute_none', message))
                    if user:
                        tim = who[1]
                        if tim:
                            if len(tim) != 2:
                                return await utils.answer(message, self.strings('no_args', message))
                            num = ''
                            t = ''
                            for q in tim:
                                if q.isdigit():
                                    num += q
                                else:
                                    t += q

                            text = f'<b>{num}'
                            if t == 'm':
                                num = int(num) * 60
                                text += ' минут(-ы).</b>'
                            elif t == 'h':
                                num = int(num) * 3600
                                text += ' час(-а/-ов).</b>'
                            elif t == 'd':
                                num = int(num) * 86400
                                text += ' дня(-ей).</b>'
                            else:
                                return await utils.answer(message, self.strings('no_args', message))
                            timee = ChatBannedRights(until_date=time.time() + int(num), send_messages=True)
                            try:
                                await message.client(EditBannedRequest(message.chat_id, user.id, timee))
                                await utils.answer(message, self.strings('muted', message).format(
                                    utils.escape_html(user.first_name)) + text)
                                return
                            except:
                                await utils.answer(message, self.strings('no_rights', message))
                        else:
                            timee = ChatBannedRights(until_date=True, send_messages=True)
                            await message.client(EditBannedRequest(message.chat_id, user.id, timee))
                            await message.edit('<b>{} теперь в муте.</b>'.format(user.first_name))
                            return

                tim = utils.get_args(message)
                if tim:
                    if len(tim[0]) < 2:
                        return await utils.answer(message, self.strings('no_args', message))
                    num = ''
                    t = ''
                    for q in tim[0]:
                        if q.isdigit():
                            num += q
                        else:
                            t += q

                    text = f'<b>{num}'
                    if t == 'm':
                        num = int(num) * 60
                        text += ' минут(-ы).</b>'
                    elif t == 'd':
                        num = int(num) * 86400
                        text += ' дня(-ей) .</b>'
                    elif t == 'h':
                        num = int(num) * 3600
                        text += ' час(-а/-ов).</b>'
                    else:
                        return await utils.answer(message, self.strings('no_args', message))
                    timee = ChatBannedRights(until_date=time.time() + int(num), send_messages=True)
                    await message.client(EditBannedRequest(message.chat_id, user.id, timee))
                    await utils.answer(message,
                                       self.strings('muted', message).format(utils.escape_html(user.first_name)) + text)
                    return
                else:
                    timee = ChatBannedRights(until_date=True, send_messages=True)
                    await message.client(EditBannedRequest(message.chat_id, user.id, timee))
                    await message.edit('<b>{} теперь в муте.</b>'.format(user.first_name))
                    return
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
            except UserAdminInvalidError:
                return await utils.answer(message, self.strings('no_rights', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def unmutecmd(self, message):
        """Команда .unmute для размута пользователя.\nИспользование: .unmute <@ или реплай>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args(message)
                    if not args:
                        return await utils.answer(message, self.strings('unmute_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                await message.client(EditBannedRequest(message.chat_id, user.id, UNMUTE_RIGHTS))
                return await utils.answer(message, self.strings('unmuted', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def delallmsgscmd(self, message):
        """Команда .delallmsgs удаляет все сообщения от пользователя.\nИспользование: .delallmsgs <@ или реплай>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не админ здесь.</b>")
            else:
                if chat.admin_rights.delete_messages == False:
                    return await message.edit("<b>У меня нет нужных прав.</b>")
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            return await utils.answer(message, self.strings('no_args_or_reply', message))
        await utils.answer(message, self.strings('deleting', message))
        if args:
            user = await message.client.get_entity(args)
        if reply:
            user = await message.client.get_entity(reply.sender_id)
        await message.client(DeleteUserHistoryRequest(message.to_id, user.id))
        await message.client.send_message(message.to_id, self.strings('deleted', message).format(user.first_name))

    async def deluserscmd(self, message):
        """Команда .delusers показывает список всех удалённых аккаунтов в чате.\nИспользование: .delusers <clean>."""
        if not message.is_group:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))
            return
        con = utils.get_args_raw(message)
        del_u = 0
        del_status = '<b>Нет удалённых аккаунтов, чат очищен.</b>'
        if con != "clean":
            await utils.answer(message, self.strings('del_u_search', message))
            async for user in message.client.iter_participants(message.chat_id):
                if user.deleted:
                    del_u += 1
            if del_u == 1:
                del_status = f"<b>Найден {del_u} удаленный аккаунт в чате, очистите их с помощью </b><code>.delusers clean</code><b>.</b>"
            if del_u > 0:
                del_status = f"<b>Найдено {del_u} удаленных аккаунтов в чате, очистите их с помощью </b><code>.delusers clean</code><b>.</b>"
            return await message.edit(del_status)
        chat = await message.get_chat()
        if not chat.admin_rights and not chat.creator:
            return await utils.answer(message, self.strings('not_admin', message))
        else:
            if chat.admin_rights.ban_users == False:
                return await utils.answer(message, self.strings('no_rights', message))
        await utils.answer(message, self.strings('del_u_kicking', message))
        del_u = 0
        del_a = 0
        async for user in message.client.iter_participants(message.chat_id):
            if user.deleted:
                try:
                    await message.client(EditBannedRequest(message.chat_id, user.id, BANNED_RIGHTS))
                except UserAdminInvalidError:
                    del_u -= 1
                    del_a += 1
                await message.client(EditBannedRequest(message.chat_id, user.id, UNBAN_RIGHTS))
                del_u += 1
        if del_u == 1:
            del_status = f"<b>Кикнут {del_u} удалённый аккаунт.</b>"
        if del_u > 0:
            del_status = f"<b>Кикнуто {del_u} удалённых аккаунтов.</b>"

        if del_a == 1:
            del_status = f"<b>Кикнут {del_u} удалённый аккаунт.\n" \
                         f"{del_a} удалённый аккаунт админа не кикнут.</b>"
        if del_a > 0:
            del_status = f"<b>Кикнуто {del_u} удалённых аккаунтов.\n" \
                         f"{del_a} удалённых аккаунта админов не кикнуты.</b>"
        await message.edit(del_status)


def resizepic(reply):
    im = Image.open(io.BytesIO(reply))
    w, h = im.size
    x = min(w, h)
    x_ = (w - x) // 2
    y_ = (h - x) // 2
    _x = x_ + x
    _y = y_ + x
    im = im.crop((x_, y_, _x, _y))
    out = io.BytesIO()
    out.name = "outsuder.png"
    im.save(out)
    return out.getvalue()


async def check_media(message, reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.video:
            data = reply.video
        elif reply.document:
            if reply.gif or reply.audio or reply.voice:
                return None
            data = reply.media.document
        else:
            return None
    else:
        return None
    if not data or data is None:
        return None
    else:
        data = await message.client.download_file(data, bytes)
        try:
            Image.open(io.BytesIO(data))
            return data
        except:
            return None
