
from pyrogram import Client, filters
import datetime
import time
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages
import asyncio
        
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    users = await db.get_all_notif_user()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Mesajı yayınlıyorum...'
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed =0
    success = 0
    async for user in users:
        pti, sh = await broadcast_messages(int(user['id']), b_msg)
        if pti:
            success += 1
        elif pti == False:
            if sh == "Blocked":
                blocked+=1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        await asyncio.sleep(2)
        if not done % 20:
            await sts.edit(f"Yayın devam ediyor:\n\nToplam Kullanıcılar {total_users}\nTamamlanan: {done} / {total_users}\nBasarılı: {success}\nEngellemis: {blocked}\nSilmis: {deleted}")
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Yayın Tamamlandı:\n{time_taken} saniye içinde tamamlandı.\n\nToplam Kullanıcılar {total_users}\nTamamlanan: {done} / {total_users}\nBasarılı: {success}\nEngellemis: {blocked}\nSilmis: {deleted}")


@Client.on_message(filters.command("ayarlar") & filters.user(ADMINS))
async def opensettings(bot, message):
    user_id = message.from_user.id
    await message.reply_text(
        f"`Bildirimleri Buradan Ayarlayabilirsiniz:`\n\nBildirimler: **{'Açık 🔔' if ((await db.get_notif(user_id)) is True) else 'Kapalı 🔕'}**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"{'🔔' if ((await db.get_notif(user_id)) is True) else '🔕'}",
                        callback_data="notifon",
                    )
                ],
                [InlineKeyboardButton("✖ İptal", callback_data="closeMeh")],
            ]
        ),
    )