import html
from typing import Optional

from telegram import Bot, Chat, ChatPermissions, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import mention_html

from FallenRobot import LOGGER, TIGERS, dispatcher
from FallenRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    user_admin,
)
from FallenRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from FallenRobot.modules.helper_funcs.string_handling import extract_time
from FallenRobot.modules.log_channel import loggable


def check_user(user_id: int, bot: Bot, chat: Chat) -> Optional[str]:
    if not user_id:
        reply = "Siz istifadəçiyə istinad etmirsiniz və ya göstərilən ID səhvdir.."
        return reply

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            reply = "Bu istifadəçini tapa bilmirəm"
            return reply
        else:
            raise

    if user_id == bot.id:
        reply = "Özümü susdurmayacağam, Sən nə qədərdə malsan 🤣?"
        return reply

    if is_user_admin(chat, user_id, member) or user_id in TIGERS:
        reply = "bilməz. Səssiz etmək üçün başqa birini tapın, lakin bu deyil."
        return reply

    return None


@connection_status
@bot_admin
@user_admin
@loggable
def mute(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, chat)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#Səssiz\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>İstifadəçi:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    if reason:
        log += f"\n<b>Səbəb:</b> {reason}"

    if member.can_send_messages is None or member.can_send_messages:
        chat_permissions = ChatPermissions(can_send_messages=False)
        bot.restrict_chat_member(chat.id, user_id, chat_permissions)
        bot.sendMessage(
            chat.id,
            f"Səssiz <b>{html.escape(member.user.first_name)}</b> son istifadə tarixi olmadan!",
            parse_mode=ParseMode.HTML,
        )
        return log

    else:
        message.reply_text("Bu istifadəçi artıq səssizdir!")

    return ""


@connection_status
@bot_admin
@user_admin
@loggable
def unmute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "Ya səsi açmaq üçün mənə istifadəçi adı verməlisən, ya da kiməsə cavab verməlisən."
        )
        return ""

    member = chat.get_member(int(user_id))

    if member.status != "kicked" and member.status != "left":
        if (
            member.can_send_messages
            and member.can_send_media_messages
            and member.can_send_other_messages
            and member.can_add_web_page_previews
        ):
            message.reply_text("Bu istifadəçinin artıq danışmaq hüququ var.")
        else:
            chat_permissions = ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
            try:
                bot.restrict_chat_member(chat.id, int(user_id), chat_permissions)
            except BadRequest:
                pass
            bot.sendMessage(
                chat.id,
                f"icazə verim <b>{html.escape(member.user.first_name)}</b> mətnə!",
                parse_mode=ParseMode.HTML,
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#Səsizi söndürün\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>isdifadəçi:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        message.reply_text(
            "Bu istifadəçi hətta çatda deyil, onların səsini açmaq onları onlardan çox danışmağa vadar etməyəcək "
            "artıq et!"
        )

    return ""


@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def temp_mute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, chat)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    if not reason:
        message.reply_text("Bu istifadəçinin səsini söndürmək üçün vaxt təyin etməmisiniz!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    mutetime = extract_time(message, time_val)

    if not mutetime:
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#Temp susduruldu\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>isdifadəçi:</b> {mention_html(member.user.id, member.user.first_name)}\n"
        f"<b>Vaxt:</b> {time_val}"
    )
    if reason:
        log += f"\n<b>Səbəb:</b> {reason}"

    try:
        if member.can_send_messages is None or member.can_send_messages:
            chat_permissions = ChatPermissions(can_send_messages=False)
            bot.restrict_chat_member(
                chat.id, user_id, chat_permissions, until_date=mutetime
            )
            bot.sendMessage(
                chat.id,
                f"Səssiz <b>{html.escape(member.user.first_name)}</b> for {time_val}!",
                parse_mode=ParseMode.HTML,
            )
            return log
        else:
            message.reply_text("Bu istifadəçi artıq səssizdir.")

    except BadRequest as excp:
        if excp.message == "Cavab mesajı tapılmadı":
            # Do not reply
            message.reply_text(f"Üçün səsi kəsildi {time_val}!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "%s səbəbiylə %s (%s) söhbətində %s istifadəçisinin səsi söndürüldü",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Lənət olsun, mən o istifadəçinin səsini söndürə bilmirəm.")

    return ""


__help__ = """
*Yalnız adminlər:*

 ❍ /mute <istifadəçi tutumu>*:* sistifadəçi ilə əlaqə saxlayır. Cavab kimi də istifadə edilə bilər, istifadəçiyə verilən cavabı susdurmaq olar.
 ❍ /tmute <istifadəçi tutumu> x(m/h/d)*:* istifadəçini x dəfə səssizləşdirir. (sap və ya cavab vasitəsilə). m = minutes , h = hours , d = `günlər`.
 ❍ /unmute <istifadəçi tutumu>*:* istifadəçinin səsini açır. Cavab kimi də istifadə edilə bilər, istifadəçiyə verilən cavabı susdurmaq olar.
"""

MUTE_HANDLER = CommandHandler("mute", mute, run_async=True)
UNMUTE_HANDLER = CommandHandler("unmute", unmute, run_async=True)
TEMPMUTE_HANDLER = CommandHandler(["tmute", "tempmute"], temp_mute, run_async=True)

dispatcher.add_handler(MUTE_HANDLER)
dispatcher.add_handler(UNMUTE_HANDLER)
dispatcher.add_handler(TEMPMUTE_HANDLER)

__mod_name__ = "Səssiz"
__handlers__ = [MUTE_HANDLER, UNMUTE_HANDLER, TEMPMUTE_HANDLER]
