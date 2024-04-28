import importlib
import re
import time
from platform import python_version as y
from sys import argv

from pyrogram import __version__ as pyrover
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram import __version__ as telever
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from telethon import __version__ as tlhver

import FallenRobot.modules.sql.users_sql as sql
from FallenRobot import (
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)
from FallenRobot.modules import ALL_MODULES
from FallenRobot.modules.helper_funcs.chat_status import is_user_admin
from FallenRobot.modules.helper_funcs.misc import paginate_modules


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
*Salam* {}, 🥀

*๏ Mənim Adım* {} !
➻ Bəzi zəhmli və faydalı xüsusiyyətləri olan ən güclü teleqram qrup idarəetmə botuyam

──────────────────
*๏ Modullarım və əmrlərim haqqında məlumat almaq üçün kömək düyməsini klikləyin.*
"""

buttons = [
    [
        InlineKeyboardButton(
            text="Məni Qrupuna Əlavə Et",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="Kömək & Əmirlərim", callback_data="help_back"),
    ],
    [
        InlineKeyboardButton(text="Haqimda" callback_data="fallen_"),
        InlineKeyboardButton(text="Kömək Qrupu", url=f"https://t.me/{SUPPORT_CHAT}"),
    ],
    [
        InlineKeyboardButton(text="✅ Qurucum ✅", url=f"tg://user?id={OWNER_ID}"),
        InlineKeyboardButton(text="☁️Mənbə☁️", callback_data="source_"),
    ],
]

HELP_STRINGS = f"""
*» {BOT_NAME} Eksklüziv xüsusiyyətlər*

➲ /start : Məni başlat | Mənə görə sən bunu artıq etmisənᴛ.
➲ /help  : Mövcud əmrlər bölməsi.
  ‣ pm-də: bütün dəstəklənən modullar üçün sizə yardım göndərəcək.
  ‣ qrupda: bütün yardım modulları ilə sizi pm-ə yönləndirəcəkꜱ."""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("FallenRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Eyni ada malik iki modul ola bilməz! Zəhmət olmasa birini dəyişdirin")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower() == "markdownhelp":
                IMPORTED["exᴛʀᴀs"].markdown_help_sender(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rᴜʟᴇs" in IMPORTED:
                IMPORTED["rᴜʟᴇs"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_sticker(
                "CAACAgIAAxkBAAEBwl5mLUPTQHOAupPbSY4X1D3eUd3l-AACKgsAAp_oOUu9V8Lq7GCYKB4E"
            )
            update.effective_message.reply_text(
                PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_photo(
            START_IMG,
            caption="Bu gün oyandığma sevndim!\n<b>o vaxtdan yatmadim​:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Xətanı daxil edin və tərtibatçıya məlumat vermək üçün teleqram mesajı göndərin."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Yeniləməni idarə edərkən istisna:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "Yeniləmə işlənərkən istisna qaldırıldı\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "» *üçün mövcud əmrlər* *{}* :\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        context.bot.answer_callback_query(query.id)

    except BadRequest:
        pass


def Fallen_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "fallen_":
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
            text=f"*Salam,*🥀\n  *Mənim Adım {BOT_NAME}*"
            "\n*Qrupunuzu asanlıqla idarə etmək və qrupunuzu fırıldaqçılardan və spamerlərdən qorumaq üçün yaradılmış güclü qrup idarəetmə botu.*"
            "\n*Məlumat bazası olaraq sqlalchemy və mongodb ilə pythonda yazılmışdır.*"
            "\n\n────────────────────"
            f"\n*➻ İş vaxtı »* {uptime}"
            f"\n*➻ İstifadəçilər »* {sql.num_users()}"
            f"\n*➻ Söhbətlər »* {sql.num_chats()}"
            "\n────────────────────"
            "\n\n➲ istifadəçiləri məhdudlaşdıra bilərəm."
            "\n➲ Təkmil anti-daşqın sistemim var."
            "\n➲ istifadəçiləri fərdiləşdirilə bilən salamlama mesajları ilə salamlaya və hətta qrup qaydalarını təyin edə bilərəm."
            "\n➲ kimi hər bir əvvəlcədən təyin edilmiş hərəkətlə xəbərdarlıq edən maksimuma çatana qədər istifadəçiləri xəbərdar edə bilərəm Ban, Mute, Kick, Etc."
            "\n➲ Sistemin qara siyahılarını və hətta müəyyən açar sözlər üzrə əvvəlcədən müəyyən edilmiş cavabları saxlayan qeydlərim var."
            f"\n\n➻ Əsas yardım və məlumat almaq üçün aşağıda verilmiş düymələrə klikləyin {BOT_NAME}.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Köməkçi Qrup", callback_data="fallen_support"
                        ),
                        InlineKeyboardButton(
                            text="ᴄᴏᴍᴍᴀɴᴅs", callback_data="help_back"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Qurucum", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="Mənbə",
                            callback_data="source_",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="fallen_back"),
                    ],
                ]
            ),
        )
    elif query.data == "fallen_support":
        query.message.edit_text(
            text="*๏ Haqqımda kömək və əlavə məlumat almaq üçün aşağıda verilmiş düymələrə klikləyin.*"
            f"\n\nƏgər hər hansı bir səhv tapsanız {BOT_NAME} Və ya bu barədə rəy bildirmək istəyirsinizsə {BOT_NAME},Zəhmət olmasa bunu dəstək çatında bildirin.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Köməkçi Qrupu", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                        InlineKeyboardButton(
                            text="Yeniləmələr", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Qrucum", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="ɢɪᴛʜᴜʙ",
                            url="https://github.com/Qadirnesirov",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="fallen_"),
                    ],
                ]
            ),
        )
    elif query.data == "fallen_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=True,
        )


def Source_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text=f"""
*Salam,
 Mənim Adım {BOT_NAME},
Açıq mənbəli teleqram qrupu idarəetmə botuyam.*

Zatranın köməyi ilə python dilində yazılmışdır :[Telemarafon](https://github.com/LonamiWebs/Telethon)
[piroqram](https://github.com/pyrogram/pyrogram)
[Python-teleqram-botu](https://github.com/python-telegram-bot/python-telegram-bot)
Və istifadə [Sqlalchemy](https://www.sqlalchemy.org) Və [MongoDB](https://cloud.mongodb.com) Verilənlər bazası kimi.


*Budur mənim mənbə kodum :* [ɢɪᴛʜᴜʙ](https://github.com/Qadirnesirov)


{BOT_NAME} Altında lisenziyaya malikdir [İlə lisenziyalıdır](https://github.com/Qadirnesirov/ZatraBot/blob/master/LICENSE).
© 2022 - 2023 | [Köməkçi Qrupu](https://t.me/{SUPPORT_CHAT}), Bütün hüquqlar qorunur.
""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="source_back")]]
            ),
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=True,
        )


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Kömək üçün PM ilə əlaqə saxlayın {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Kömək",
                                url="https://t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "» Yardım almaq üçün bir seçim yolu seçin.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Şəxsi açın",
                            url="https://t.me/{}?start=help".format(
                                context.bot.username
                            ),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Burada açın",
                            callback_data="help_back",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Sizin üçün mövcud yardım buradadır*{}* modul:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "Bunlar cari parametrlərinizdir:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Görünür, hər hansı bir istifadəçi üçün xüsusi parametrlər mövcud deyil 🥲",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="{}' parametrlərini hansı modul üçün yoxlamaq istərdiniz?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Deyəsən, heç bir söhbət parametri mövcud deyil :'(\nBunu göndər"
                "qrup çatında onun cari parametrlərini tapmaq üçün admin olduğunuz!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* üçün aşağıdakı parametrlərə malikdir *{}* modul:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="◁",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "salam! Sizin üçün kifayət qədər bir neçə parametr var {} - gedin və nəyi seçin "
                "maraqlanırsınız.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "salam! Sizin üçün kifayət qədər bir neçə parametr var {} - gedin və nəyi seçin "
                "maraqlanırsınız.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="salam! sizin üçün kifayət qədər bir neçə parametr var {} - gedin və nəyi seçin "
                "maraqlanırsınız.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Mesaj dəyişdirilməyib",
            "Sorğu_idi_etibarsızdır",
            "Mesaj silinə bilməz",
        ]:
            LOGGER.exception("Parametrlər düymələrində istisna. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Bu söhbətin, eləcə də sizin ayarlarınızı əldə etmək üçün bura klikləyin."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Parametrlər",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Parametrlərinizi yoxlamaq üçün bura klikləyin."

    else:
        send_settings(chat.id, user.id, True)


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("%s-dən %s-ə köçürülür", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Uğurla köçdü!")
    raise DispatcherHandlerStop


def main():
    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                chat_id=f"@{SUPPORT_CHAT}",
                photo=START_IMG,
                caption=f"""
ㅤ🥀 {BOT_NAME} Bu gün oyanmağa sevindim...

┏•❅────✧❅✦❅✧────❅•┓
| ★ **ᴘʏᴛʜᴏɴ :** `{y()}`
| ★ **ʟɪʙʀᴀʀʏ :** `{telever}`
| ★ **ᴛᴇʟᴇᴛʜᴏɴ :** `{tlhver}`
| ★ **ᴩʏʀᴏɢʀᴀᴍ :** `{pyrover}`
┗•❅────✧❅✦❅✧────❅•┛""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot mesaj göndərə bilmir @{SUPPORT_CHAT}, gedin yoxlayın!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    about_callback_handler = CallbackQueryHandler(
        Fallen_about_callback, pattern=r"fallen_", run_async=True
    )
    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )

    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)

    dispatcher.add_error_handler(error_callback)

    LOGGER.info("Uzun sorğudan istifadə.")
    updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Modullar uğurla yükləndi: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
