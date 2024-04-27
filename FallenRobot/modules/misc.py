from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Filters

from FallenRobot import dispatcher
from FallenRobot.modules.disable import DisableAbleCommandHandler
from FallenRobot.modules.helper_funcs.chat_status import user_admin

MARKDOWN_HELP = f"""
Markdown telegram tərəfindən dəstəklənən çox güclü formatlama vasitəsidir. {dispatcher.bot.first_name} əmin olmaq üçün bəzi təkmilləşdirmələrə malikdir \
saxlanmış mesajlar düzgün təhlil edilir və düymələr yaratmağa imkan verir.

• <code>_italic_</code>: mətni '_' ilə bükmək kursiv mətn yaradacaq
• <code>*bold*</code>: mətni '*' ilə bükmək qalın mətn yaradacaq
• <code>`code`</code>: mətnin '`' ilə bükülməsi monoboşluqlu mətn yaradacaq 'code'
• <code>[sometext](someURL)</code>: bu, bir keçid yaradacaq - mesaj sadəcə görünəcək <code>sometext</code>, \
və üzərinə toxunmaq səhifəni açacaq <code>someURL</code>.
<b>Example:</b><code>[test](example.com)</code>

• <code>[buttontext](buttonurl:someURL)</code>: bu, istifadəçilərə teleqrama sahib olmaq üçün xüsusi təkmilləşdirmədir \
onların işarələmələrindəki düymələr. <code>buttontext</code> düymədə göstərilənlər olacaq və <code>someurl</code> \
açılan url olacaq.
<b>Example:</b> <code>[This is a button](buttonurl:example.com)</code>

Eyni sətirdə bir neçə düyməni istəyirsinizsə, istifadə edin :same, kimi such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
Bu, hər sətirdə bir düymə əvəzinə, bir sətirdə iki düymə yaradacaqdır.

Mesajınız olduğunu unutmayın <b>olmalıdır</b> sadəcə düymədən başqa bəzi mətnləri ehtiva edir!
"""


@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1], quote=False, parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Aşağıdakı mesajı mənə yönləndirməyə çalışın və siz görəcəksiniz və #test istifadə edin!"
    )
    update.effective_message.reply_text(
        "/save test Bu işarələmə testidir. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "özəl":
        update.effective_message.reply_text(
            "pm ilə əlaqə saxlayın",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Markdown yardımı",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        )
                    ]
                ]
            ),
        )
        return
    markdown_help_sender(update)


__help__ = """
*Mövcud əmrlər:*
*Markdown:*
 ❍ /markdownhelp*:* teleqramda markdownun necə işlədiyinə dair qısa xülasə - yalnız şəxsi söhbətlərdə zəng etmək olar
*Reaksiya:*
 ❍ /react*:* Təsadüfi reaksiya ilə reaksiya verir
*Şəhər Diktoniyası:*
 ❍ /ud <Söz>*:* Axtarmaq istədiyiniz sözü və ya ifadəni yazın
*Wikipedia:*
 ❍ /wiki <Sorğu>*:* wikipedia sorğunuz
"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True
)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, run_async=True)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)

__mod_name__ = "Əlavələr"
__command_list__ = ["id", "echo"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
]
