import math

import pynewtonmath as newton
from telegram import Update
from telegram.ext import CallbackContext

from FallenRobot import dispatcher
from FallenRobot.modules.disable import DisableAbleCommandHandler


def simplify(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.simplify("{}".format(args[0])))


def factor(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.factor("{}".format(args[0])))


def derive(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.derive("{}".format(args[0])))


def integrate(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.integrate("{}".format(args[0])))


def zeroes(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.zeroes("{}".format(args[0])))


def tangent(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.tangent("{}".format(args[0])))


def area(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(newton.area("{}".format(args[0])))


def cos(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.cos(int(args[0])))


def sin(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.sin(int(args[0])))


def tan(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.tan(int(args[0])))


def arccos(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.acos(int(args[0])))


def arcsin(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.asin(int(args[0])))


def arctan(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.atan(int(args[0])))


def abs(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.fabs(int(args[0])))


def log(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    message.reply_text(math.log(int(args[0])))


__help__ = """
*Riyaziyyat*
istifadə edərək mürəkkəb riyazi məsələləri həll edir https://newton.now.sh
❍ /math*:* Riyaziyyat`/math 2^2+2(2)`
❍ /factor*:* Amil `/factor x^2 + 2x`
❍ /derive*:* Alın `/derive x^2+2x`
❍ /integrate*:* İnteqrasiya edin `/integrate x^2+2x`
❍ /zeroes*:* 0-ları tapın`/zeroes x^2+2x`
❍ /tangent*:* Tangens tapın`/tangent 2lx^3`
❍ /area*:* Əyri altındakı sahə`/area 2:4lx^3`
❍ /cos*:* Kosinus`/cos pi`
❍ /sin*:* Onun`/sin 0`
❍ /tan*:* Tangens `/tan 0`
❍ /arccos*:* Tərs kosinus`/arccos 1`
❍ /arcsin*:* Tərs sinus`/arcsin 0`
❍ /arctan*:* Tərs tangens`/arctan 0`
❍ /abs*:* Mütləq dəyər`/abs -1`
❍ /log*:* Loqarifm`/log 2l8`

_Yadında saxla_: Müəyyən x dəyərində funksiyanın tangens xəttini tapmaq üçün sorğunu c|f(x) kimi göndərin, burada c verilmiş x dəyəridir və f(x) funksiya ifadəsidir, ayırıcı şaquli sətirdir '|' . Nümunə sorğu üçün yuxarıdakı cədvələ baxın.
Funksiya altındakı sahəni tapmaq üçün sorğunu c:d|f(x) kimi göndərin, burada c başlanğıc x dəyəri, d son x dəyəri və f(x) arasında əyrinin olmasını istədiyiniz funksiyadır. iki x dəyəri.
Kəsrləri hesablamaq üçün ifadələri say(üst) məxrəc kimi daxil edin. Məsələn, 2/4-ü emal etmək üçün ifadənizi 2(over)4 kimi göndərməlisiniz. Nəticə ifadəsi standart riyaziyyat qeydində olacaq (1/2, 3/4).
"""

__mod_name__ = "Riyaziyyat"

SIMPLIFY_HANDLER = DisableAbleCommandHandler("math", simplify, run_async=True)
FACTOR_HANDLER = DisableAbleCommandHandler("factor", factor, run_async=True)
DERIVE_HANDLER = DisableAbleCommandHandler("derive", derive, run_async=True)
INTEGRATE_HANDLER = DisableAbleCommandHandler("integrate", integrate, run_async=True)
ZEROES_HANDLER = DisableAbleCommandHandler("zeroes", zeroes, run_async=True)
TANGENT_HANDLER = DisableAbleCommandHandler("tangent", tangent, run_async=True)
AREA_HANDLER = DisableAbleCommandHandler("area", area, run_async=True)
COS_HANDLER = DisableAbleCommandHandler("cos", cos, run_async=True)
SIN_HANDLER = DisableAbleCommandHandler("sin", sin, run_async=True)
TAN_HANDLER = DisableAbleCommandHandler("tan", tan, run_async=True)
ARCCOS_HANDLER = DisableAbleCommandHandler("arccos", arccos, run_async=True)
ARCSIN_HANDLER = DisableAbleCommandHandler("arcsin", arcsin, run_async=True)
ARCTAN_HANDLER = DisableAbleCommandHandler("arctan", arctan, run_async=True)
ABS_HANDLER = DisableAbleCommandHandler("abs", abs, run_async=True)
LOG_HANDLER = DisableAbleCommandHandler("log", log, run_async=True)

dispatcher.add_handler(SIMPLIFY_HANDLER)
dispatcher.add_handler(FACTOR_HANDLER)
dispatcher.add_handler(DERIVE_HANDLER)
dispatcher.add_handler(INTEGRATE_HANDLER)
dispatcher.add_handler(ZEROES_HANDLER)
dispatcher.add_handler(TANGENT_HANDLER)
dispatcher.add_handler(AREA_HANDLER)
dispatcher.add_handler(COS_HANDLER)
dispatcher.add_handler(SIN_HANDLER)
dispatcher.add_handler(TAN_HANDLER)
dispatcher.add_handler(ARCCOS_HANDLER)
dispatcher.add_handler(ARCSIN_HANDLER)
dispatcher.add_handler(ARCTAN_HANDLER)
dispatcher.add_handler(ABS_HANDLER)
dispatcher.add_handler(LOG_HANDLER)
