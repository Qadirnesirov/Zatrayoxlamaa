from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram import __version__ as telever
from telethon import __version__ as tlhver

from FallenRobot import BOT_NAME, BOT_USERNAME, OWNER_ID, START_IMG, SUPPORT_CHAT, pbot


@pbot.on_message(filters.command("alive"))
async def awake(_, message: Message):
    TEXT = f"**sᴀʟᴀᴍ {message.from_user.mention},\n\nᴍəɴ {BOT_NAME}**\n━━━━━━━━━━━━━━━━━━━\n\n"
    TEXT += f"» **Məɴɪᴍ Qᴜʀᴜᴄᴜᴍ :** [乙 卂 ㄒ 尺 卂](tg://user?id={OWNER_ID})\n\n"
    TEXT += f"» **ᴠᴇʀsɪʏᴀ ᴋɪᴛᴀʙxᴀɴᴀsı :** `{telever}` \n\n"
    TEXT += f"» **Tᴇʟᴇᴍᴀʀᴀғᴏɴ ᴠᴇʀsɪʏᴀsᴏɴ :** `{tlhver}` \n\n"
    TEXT += f"» **Pɪʀᴏǫʀᴀᴍ ᴠᴇʀsɪʏᴀsı :** `{pyrover}` \n━━━━━━━━━━━━━━━━━\n\n"
    BUTTON = [
        [
            InlineKeyboardButton("Kömək", url=f"https://t.me/{BOT_USERNAME}?start=help"),
            InlineKeyboardButton("Köməkçi Qrup", url=f"https://t.me/{SUPPORT_CHAT}"),
        ]
    ]
    await message.reply_photo(
        photo=START_IMG,
        caption=TEXT,
        reply_markup=InlineKeyboardMarkup(BUTTON),
    )


__mod_name__ = "işləyirəm"
