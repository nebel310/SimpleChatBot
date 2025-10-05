import logging
from aiogram import Bot, types, F
from aiogram.types import ContentType
from database import save_message_link, is_user_banned, get_user
from utils import format_user_info
from config import ADMIN_ID

logger = logging.getLogger(__name__)

async def handle_user_text(message: types.Message, bot: Bot):
    if is_user_banned(message.from_user.id):
        return

    # Если это кнопка "Просто общаться" - игнорируем
    if message.text == "📞 Просто общаться":
        await message.answer("Отлично! Просто пиши мне сообщения - я отвечу!")
        return

    user = message.from_user
    
    admin_text = f"{format_user_info(user.id, message.chat.id)}\n\n"
    admin_text += f"💬 Сообщение: {message.text}"

    admin_message = await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text
    )

    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )

    logger.info(f"Переслано текстовое сообщение от {user.username}")

async def handle_user_photo(message: types.Message, bot: Bot):
    if is_user_banned(message.from_user.id):
        return

    user = message.from_user
    
    admin_text = f"{format_user_info(user.id, message.chat.id)}\n\n"
    admin_text += f"📷 Фото"
    if message.caption:
        admin_text += f"\n📝 Подпись: {message.caption}"

    admin_message = await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=admin_text
    )

    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )

    logger.info(f"Переслано фото от {user.username}")

async def handle_user_voice(message: types.Message, bot: Bot):
    if is_user_banned(message.from_user.id):
        return

    user = message.from_user
    
    admin_text = f"{format_user_info(user.id, message.chat.id)}\n\n"
    admin_text += f"🎤 Голосовое сообщение"

    admin_message = await bot.send_voice(
        chat_id=ADMIN_ID,
        voice=message.voice.file_id,
        caption=admin_text
    )

    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )

    logger.info(f"Переслано голосовое от {user.username}")

async def handle_user_document(message: types.Message, bot: Bot):
    if is_user_banned(message.from_user.id):
        return

    user = message.from_user
    
    admin_text = f"{format_user_info(user.id, message.chat.id)}\n\n"
    admin_text += f"📎 Документ: {message.document.file_name}"
    if message.caption:
        admin_text += f"\n📝 Подпись: {message.caption}"

    admin_message = await bot.send_document(
        chat_id=ADMIN_ID,
        document=message.document.file_id,
        caption=admin_text
    )

    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )

    logger.info(f"Переслан документ от {user.username}")

async def handle_user_video(message: types.Message, bot: Bot):
    if is_user_banned(message.from_user.id):
        return

    user = message.from_user
    
    admin_text = f"{format_user_info(user.id, message.chat.id)}\n\n"
    admin_text += f"🎥 Видео"
    if message.caption:
        admin_text += f"\n📝 Подпись: {message.caption}"

    admin_message = await bot.send_video(
        chat_id=ADMIN_ID,
        video=message.video.file_id,
        caption=admin_text
    )

    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )

    logger.info(f"Переслано видео от {user.username}")

async def handle_user_sticker(message: types.Message, bot: Bot):
    if is_user_banned(message.from_user.id):
        return

    user = message.from_user
    
    admin_text = f"{format_user_info(user.id, message.chat.id)}\n\n"
    admin_text += f"🩷 Стикер"

    # Сначала отправляем информацию
    info_message = await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text
    )

    # Затем стикер
    admin_message = await bot.send_sticker(
        chat_id=ADMIN_ID,
        sticker=message.sticker.file_id
    )

    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )

    logger.info(f"Переслан стикер от {user.username}")


from database import save_message_link, get_user_by_admin_message
from config import ADMIN_ID

async def handle_admin_reply(message: types.Message, bot: Bot):
    """Обработчик ответов админа на обычные сообщения (не верификация)"""
    if message.from_user.id != ADMIN_ID or not message.reply_to_message:
        return

    from database import get_user_by_admin_message
    original = get_user_by_admin_message(message.reply_to_message.message_id)
    if not original:
        await message.reply("❌ Не могу найти исходного отправителя для этого сообщения")
        return

    user_chat_id = original[3]  # chat_id пользователя
    username = original[4]      # username

    try:
        # Отправляем ответ пользователю в зависимости от типа контента
        if message.text:
            await bot.send_message(chat_id=user_chat_id, text=message.text)
        elif message.photo:
            await bot.send_photo(
                chat_id=user_chat_id,
                photo=message.photo[-1].file_id,
                caption=message.caption
            )
        elif message.voice:
            await bot.send_voice(chat_id=user_chat_id, voice=message.voice.file_id)
        elif message.video_note:
            await bot.send_video_note(chat_id=user_chat_id, video_note=message.video_note.file_id)
        elif message.sticker:
            await bot.send_sticker(chat_id=user_chat_id, sticker=message.sticker.file_id)
        elif message.document:
            await bot.send_document(
                chat_id=user_chat_id,
                document=message.document.file_id,
                caption=message.caption
            )
        elif message.video:
            await bot.send_video(
                chat_id=user_chat_id,
                video=message.video.file_id,
                caption=message.caption
            )
        else:
            await message.reply("❌ Этот тип сообщения пока не поддерживается для ответа")
            return
        
        await message.reply(f"✅ Ответ отправлен пользователю @{username}")
        logger.info(f"Ответ отправлен пользователю {username}")
        
    except Exception as e:
        await message.reply(f"❌ Ошибка при отправке: {e}")
        logger.error(f"Ошибка отправки: {e}")