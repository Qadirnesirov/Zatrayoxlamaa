from platform import python_version as y

from pyrogram import __version__ as z
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram import __version__ as o
from telethon import __version__ as s

from FallenRobot import BOT_NAME, BOT_USERNAME, OWNER_ID, START_IMG, pbot


@pbot.on_message(filters.command(["repo", "ᴍəɴʙə"]))
async def repo(_, message: Message):
    await message.reply_photo(
        photo=START_IMG,
        caption=f"""**sᴀʟᴀᴍ {message.from_user.mention},

ᴍəɴ [{BOT_NAME}](https://t.me/{BOT_USERNAME})**

**» Məɴɪᴍ Qᴜʀᴜᴄᴜᴍ :** 乙 卂 ㄒ 尺 卂
**» ᴘʏᴛʜᴏɴ ᴠᴇʀsɪʏᴀsı :** `{y()}`
**» ᴠᴇʀsɪʏᴀ ᴋɪᴛᴀʙxᴀɴᴀsı:** `{o}` 
**» Tᴇʟᴇᴍᴀʀᴀғᴏɴ ᴠᴇʀsɪʏᴀsıɴ :** `{s}` 
**» Pɪʀᴏǫʀᴀᴍ ᴠᴇʀsɪʏᴀsı :** `{z}`
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(" Qᴜʀᴜᴄᴜᴍ", user_id=OWNER_ID),
                    InlineKeyboardButton(
                        "ᴍəɴʙə",
                        url="https://github.com/Qadirnesirov/ZatraNezaret",
                    ),
                ]
            ]
        ),
    )


__mod_name__ = "Rᴇᴩᴏ"
