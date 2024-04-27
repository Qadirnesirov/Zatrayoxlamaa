from datetime import datetime
from functools import wraps

from telegram.ext import CallbackContext

from FallenRobot.modules.helper_funcs.misc import is_module_loaded

FILENAME = __name__.rsplit(".", 1)[-1]

if is_module_loaded(FILENAME):
    from telegram import ParseMode, Update
    from telegram.error import BadRequest, Unauthorized
    from telegram.ext import CommandHandler, JobQueue
    from telegram.utils.helpers import escape_markdown

    from FallenRobot import EVENT_LOGS, LOGGER, dispatcher
    from FallenRobot.modules.helper_funcs.chat_status import user_admin
    from FallenRobot.modules.sql import log_channel_sql as sql

    def loggable(func):
        @wraps(func)
        def log_action(
            update: Update,
            context: CallbackContext,
            job_queue: JobQueue = None,
            *args,
            **kwargs,
        ):
            if not job_queue:
                result = func(update, context, *args, **kwargs)
            else:
                result = func(update, context, job_queue, *args, **kwargs)

            chat = update.effective_chat
            message = update.effective_message

            if result:
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += f"\n<b>Hadisə möhürü</b>: <code>{datetime.utcnow().strftime(datetime_fmt)}</code>"

                if message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n<b>Link:</b> <a href="https://t.me/{chat.username}/{message.message_id}">Bura basın</a>'
                log_chat = sql.get_chat_log_channel(chat.id)
                if log_chat:
                    send_log(context, log_chat, chat.id, result)

            return result

        return log_action

    def gloggable(func):
        @wraps(func)
        def glog_action(update: Update, context: CallbackContext, *args, **kwargs):
            result = func(update, context, *args, **kwargs)
            chat = update.effective_chat
            message = update.effective_message

            if result:
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += "\n<b>Hadisə möhürü</b>: <code>{}</code>".format(
                    datetime.utcnow().strftime(datetime_fmt)
                )

                if message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n<b>Link:</b> <a href="https://t.me/{chat.username}/{message.message_id}">Bura basın</a>'
                log_chat = str(EVENT_LOGS)
                if log_chat:
                    send_log(context, log_chat, chat.id, result)

            return result

        return glog_action

    def send_log(
        context: CallbackContext, log_chat_id: str, orig_chat_id: str, result: str
    ):
        bot = context.bot
        try:
            bot.send_message(
                log_chat_id,
                result,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message == "Söhbət tapılmadı":
                bot.send_message(
                    orig_chat_id, "Bu log kanalı silindi - parametr ləğv edilir."
                )
                sql.stop_chat_logging(orig_chat_id)
            else:
                LOGGER.warning(excp.message)
                LOGGER.warning(result)
                LOGGER.exception("Analiz etmək mümkün olmadı")

                bot.send_message(
                    log_chat_id,
                    result
                    + "\n\nFormatlaşdırma gözlənilməz xətaya görə qeyri-aktiv edildi.",
                )

    @user_admin
    def logging(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.get_chat_log_channel(chat.id)
        if log_channel:
            log_channel_info = bot.get_chat(log_channel)
            message.reply_text(
                f"Bu qrupda göndərilən bütün qeydlər var:"
                f" {escape_markdown(log_channel_info.title)} (`{log_channel}`)",
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            message.reply_text("Bu qrup üçün heç bir jurnal kanalı təyin edilməyib!")

    @user_admin
    def setlog(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat
        if chat.type == chat.CHANNEL:
            message.reply_text(
                "İndi /setlog bu kanalı bağlamaq istədiyiniz qrupa yönləndirin!"
            )

        elif message.forward_from_chat:
            sql.set_chat_log_channel(chat.id, message.forward_from_chat.id)
            try:
                message.delete()
            except BadRequest as excp:
                if excp.message == "Silinəcək mesaj tapılmadı":
                    pass
                else:
                    LOGGER.exception(
                        "Giriş kanalında mesajı silərkən xəta baş verdi. Hər halda işləməlidir."
                    )

            try:
                bot.send_message(
                    message.forward_from_chat.id,
                    f"Bu kanal giriş kanalı kimi təyin edilib {chat.title or chat.first_name}.",
                )
            except Unauthorized as excp:
                if excp.message == "Qadağandır: bot kanal çatının üzvü deyil":
                    bot.send_message(chat.id, "Giriş kanalını uğurla quraşdırın!")
                else:
                    LOGGER.exception("Jurnal kanalının qurulmasında XƏTA.")

            bot.send_message(chat.id, "Giriş kanalını uğurla quraşdırın!")

        else:
            message.reply_text(
                "Giriş kanalı qurmaq üçün addımlar bunlardır:\n"
                " - istədiyiniz kanala botu əlavə edin\n"
                " - kanala /setlog\n"
                " - /setlog qrupa yönləndirin\n"
            )

    @user_admin
    def unsetlog(update: Update, context: CallbackContext):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.stop_chat_logging(chat.id)
        if log_channel:
            bot.send_message(
                log_channel, f"Kanalın əlaqəsi kəsildi {chat.title}"
            )
            message.reply_text("Giriş kanalı ləğv edildi.")

        else:
            message.reply_text("Hələ heç bir giriş kanalı qurulmayıb!")

    def __stats__():
        return f"• {sql.num_logchannels()} log kanalları təyin olunur."

    def __migrate__(old_chat_id, new_chat_id):
        sql.migrate_chat(old_chat_id, new_chat_id)

    def __chat_settings__(chat_id, user_id):
        log_channel = sql.get_chat_log_channel(chat_id)
        if log_channel:
            log_channel_info = dispatcher.bot.get_chat(log_channel)
            return f"Bu qrupda göndərilən bütün qeydlər var: {escape_markdown(log_channel_info.title)} (`{log_channel}`)"
        return "Bu qrup üçün heç bir jurnal kanalı təyin edilməyib!"

    __help__ = """
*Yalnız adminlər:*
 ❍ /logchannel*:* günlük kanal məlumatını əldə edin
 ❍ /setlog*:* log kanalını təyin edin.
 ❍ /unsetlog*:* log kanalını ləğv edin.

Giriş kanalının qurulması tərəfindən həyata keçirilir:
❍ botun istədiyiniz kanala əlavə edilməsi (admin olaraq!)
❍ kanalda /setlog göndərmək
❍ /setlog qrupa yönləndirmək
"""

    __mod_name__ = "Logo"

    LOG_HANDLER = CommandHandler("logchannel", logging, run_async=True)
    SET_LOG_HANDLER = CommandHandler("setlog", setlog, run_async=True)
    UNSET_LOG_HANDLER = CommandHandler("unsetlog", unsetlog, run_async=True)

    dispatcher.add_handler(LOG_HANDLER)
    dispatcher.add_handler(SET_LOG_HANDLER)
    dispatcher.add_handler(UNSET_LOG_HANDLER)

else:
    # run anyway if module not loaded
    def loggable(func):
        return func

    def gloggable(func):
        return func
