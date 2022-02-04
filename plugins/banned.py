from pyrogram import Client, filters
from utils import temp
from pyrogram.types import Message
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import SUPPORT_CHAT

async def banned_users(_, client, message: Message):
    return (
        message.from_user is not None or not message.sender_chat
    ) and message.from_user.id in temp.BANNED_USERS

banned_user = filters.create(banned_users)


@Client.on_message(filters.private & banned_user & filters.incoming)
async def ban_reply(bot, message):
    ban = await db.get_ban_status(message.from_user.id)
    await message.reply(f'Üzgünüm dostum, beni kullanman yasaklandı. \nSebep: {ban["ban_reason"]}')


@Client.on_message(filters.group & filters.incoming)
async def grp_bd(bot, message):
    buttons = [[
        InlineKeyboardButton('Korsan', url=f'https://t.me/{SUPPORT_CHAT}')
    ]]
    reply_markup=InlineKeyboardMarkup(buttons)
    k = await message.reply(
        text=f"**Ben gruplara kapalıyım dostum.**",
        reply_markup=reply_markup,
        parse_mode='markdown',
    )
    try:
        await k.pin()
        await bot.leave_chat(message.chat.id)
    except:
        pass
    await bot.leave_chat(message.chat.id)