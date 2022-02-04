import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS, LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
import re
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()


@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("İndekslemeyi İptal et")
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if raju == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'Gönderiniz moderatörlerimiz tarafından reddedildi.',
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('Önceki işlem tamamlanana kadar bekleyin.', show_alert=True)
    msg = query.message

    await query.answer('İşleniyor...⏳', show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'Gönderiniz moderatörlerimiz tarafından kabul edildi ve yakında eklenecek.',
                               reply_to_message_id=int(lst_msg_id))
    await msg.edit(
        "İndeksleme Başlatıldı",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('İptal et', callback_data='index_cancel')]]
        )
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming)
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Geçersiz link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif message.forward_from_chat.type == 'channel':
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('Bu özel bir kanal/grup olabilir. Dosyaları indekslemek için beni orada yönetici yap.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Geçersiz Bağlantı belirtildi.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'Hata - {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Kanal gizli ise Kanalda Yönetici Olduğumdan Emin Olun')
    if k.empty:
        return await message.reply('Bu grup olabilir ve ben grubun yöneticisi değilim.')

    if message.from_user.id in ADMINS:
        buttons = [
            [
                InlineKeyboardButton('Evet',
                                     callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
            ],
            [
                InlineKeyboardButton('İptal et', callback_data='close_data'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f'Bu Kanalı/Grubu İndekslemek İstiyor musunuz?\n\nKanal ID/ Username: <code>{chat_id}</code>\nSon Mesaj ID: <code>{last_msg_id}</code>',
            reply_markup=reply_markup)

    if type(chat_id) is int:
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('Sohbette yönetici olduğumdan ve kullanıcıları davet etme iznine sahip olduğumdan emin olun.')
    else:
        link = f"@{message.forward_from_chat.username}"
    buttons = [
        [
            InlineKeyboardButton('Kabul Et',
                                 callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
        ],
        [
            InlineKeyboardButton('Reddet',
                                 callback_data=f'index#reject#{chat_id}#{message.message_id}#{message.from_user.id}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(LOG_CHANNEL,
                           f'#Taleb\n\nBy : {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/ Username - <code> {chat_id}</code>\nLast Message ID - <code>{last_msg_id}</code>\nInviteLink - {link}',
                           reply_markup=reply_markup)
    await message.reply('Katkılarınız İçin Teşekkürler, Moderatörlerimin dosyaları doğrulamasını bekleyin.')


@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply("Atlama numarası bir tam sayı olmalıdır.")
        await message.reply(f"Numarasını başarıyla ayarla {skip}")
        temp.CURRENT = int(skip)
    else:
        await message.reply("Bana bir atlama numarası ver")


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    async with lock:
        try:
            total = lst_msg_id + 1
            current = temp.CURRENT
            temp.CANCEL = False
            while current < total:
                if temp.CANCEL:
                    await msg.edit("Başarıyla İptal Edildi")
                    break
                try:
                    message = await bot.get_messages(chat_id=chat, message_ids=current, replies=0)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    message = await bot.get_messages(
                        chat,
                        current,
                        replies=0
                    )
                except Exception as e:
                    logger.exception(e)
                try:
                    for file_type in ("document", "video", "audio"):
                        media = getattr(message, file_type, None)
                        if media is not None:
                            break
                        else:
                            continue
                    media.file_type = file_type
                    media.caption = message.caption
                    aynav, vnay = await save_file(media)
                    if aynav:
                        total_files += 1
                    elif vnay == 0:
                        duplicate += 1
                    elif vnay == 2:
                        errors += 1
                except Exception as e:
                    if "NoneType" in str(e):
                        if message.empty:
                            deleted += 1
                        elif not media:
                            no_media += 1
                        logger.warning("Silinen / Medya Dışı mesajları atlama (bu uzun süre devam ederse, bir atlama numarası ayarlamak için /setskip kullanın)")
                    else:
                        logger.exception(e)
                current += 1
                if current % 20 == 0:
                    can = [[InlineKeyboardButton('İptal', callback_data='index_cancel')]]
                    reply = InlineKeyboardMarkup(can)
                    await msg.edit_text(
                        text=f"Alınan toplam ileti sayısı: <code>{current}</code>\nToplam kaydedilen mesaj: <code>{total_files}</code>\nYinelenen Dosyalar Atlandı: <code>{duplicate}</code>\nSilinen Mesajlar Atlandı: <code>{deleted}</code>\nMedya dışı mesajlar atlandı: <code>{no_media}</code>\nOluşan Hatalar: <code>{errors}</code>",
                        reply_markup=reply)
        except Exception as e:
            logger.exception(e)
            await msg.edit(f'Hata: {e}')
        else:
            await msg.edit(f'Başarıyla kaydedildi <code>{total_files}</code> to dataBase!\nYinelenen Dosyalar Atlandı: <code>{duplicate}</code>\nSilinen Mesajlar Atlandı: <code>{deleted}</code>\nMedya dışı mesajlar atlandı: <code>{no_media}</code>\nOluşan Hatalar: <code>{errors}</code>')
