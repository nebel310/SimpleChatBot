import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ContentType
import sqlite3
from config import BOT_TOKEN, ADMIN_ID

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация БД
def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS message_links
                 (admin_message_id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  user_message_id INTEGER,
                  chat_id INTEGER,
                  username TEXT)''')
    conn.commit()
    conn.close()

def save_message_link(admin_message_id, user_id, user_message_id, chat_id, username):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("INSERT INTO message_links VALUES (?, ?, ?, ?, ?)",
              (admin_message_id, user_id, user_message_id, chat_id, username))
    conn.commit()
    conn.close()

def get_user_by_admin_message(admin_message_id):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT * FROM message_links WHERE admin_message_id=?", (admin_message_id,))
    result = c.fetchone()
    conn.close()
    return result

# Форматирование информации о пользователе
def format_user_info(user, chat_id):
    return (f"👤 *От:* {user.first_name or ''} {user.last_name or ''}\n"
            f"📛 @{user.username or 'нет'}\n"
            f"🆔 ID: `{user.id}`\n"
            f"💬 Chat ID: `{chat_id}`")

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🤖 Привет! Я супер-умный ИИ бот для общения. "
        "Можешь поговорить со мной на любую тему!\n\n"
        "Просто напиши что-нибудь, и я отвечу!",
        parse_mode="Markdown"
    )

# Обработчик ТЕКСТОВЫХ сообщений от пользователей
@dp.message(F.content_type == ContentType.TEXT, F.from_user.id != ADMIN_ID)
async def handle_user_text(message: Message):
    user = message.from_user
    
    # Формируем сообщение для админа
    admin_text = f"{format_user_info(user, message.chat.id)}\n\n"
    admin_text += f"💬 *Сообщение:* {message.text}"
    
    # Отправляем админу
    admin_message = await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        parse_mode="Markdown"
    )
    
    # Сохраняем связь
    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )
    
    logger.info(f"Переслано текстовое сообщение от {user.username}")

# Обработчик ФОТО от пользователей
@dp.message(F.content_type == ContentType.PHOTO, F.from_user.id != ADMIN_ID)
async def handle_user_photo(message: Message):
    user = message.from_user
    
    admin_text = f"{format_user_info(user, message.chat.id)}\n\n"
    admin_text += f"📷 *Фото*"
    if message.caption:
        admin_text += f"\n📝 *Подпись:* {message.caption}"
    
    admin_message = await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=admin_text,
        parse_mode="Markdown"
    )
    
    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )
    
    logger.info(f"Переслано фото от {user.username}")

# Обработчик ГОЛОСОВЫХ сообщений
@dp.message(F.content_type == ContentType.VOICE, F.from_user.id != ADMIN_ID)
async def handle_user_voice(message: Message):
    user = message.from_user
    
    admin_text = f"{format_user_info(user, message.chat.id)}\n\n"
    admin_text += f"🎤 *Голосовое сообщение*"
    
    admin_message = await bot.send_voice(
        chat_id=ADMIN_ID,
        voice=message.voice.file_id,
        caption=admin_text,
        parse_mode="Markdown"
    )
    
    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )
    
    logger.info(f"Переслано голосовое от {user.username}")

# Обработчик ВИДЕО сообщений
@dp.message(F.content_type == ContentType.VIDEO_NOTE, F.from_user.id != ADMIN_ID)
async def handle_user_video_note(message: Message):
    user = message.from_user
    
    admin_text = f"{format_user_info(user, message.chat.id)}\n\n"
    admin_text += f"📹 *Видео-сообщение*"
    
    admin_message = await bot.send_video_note(
        chat_id=ADMIN_ID,
        video_note=message.video_note.file_id,
        caption=admin_text
    )
    
    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )
    
    logger.info(f"Переслано видео-сообщение от {user.username}")

# Обработчик СТИКЕРОВ
@dp.message(F.content_type == ContentType.STICKER, F.from_user.id != ADMIN_ID)
async def handle_user_sticker(message: Message):
    user = message.from_user
    
    admin_text = f"{format_user_info(user, message.chat.id)}\n\n"
    admin_text += f"🩷 *Стикер*"
    
    # Сначала отправляем информацию
    info_message = await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        parse_mode="Markdown"
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

# Обработчик ДОКУМЕНТОВ
@dp.message(F.content_type == ContentType.DOCUMENT, F.from_user.id != ADMIN_ID)
async def handle_user_document(message: Message):
    user = message.from_user
    
    admin_text = f"{format_user_info(user, message.chat.id)}\n\n"
    admin_text += f"📎 *Документ:* {message.document.file_name}"
    if message.caption:
        admin_text += f"\n📝 *Подпись:* {message.caption}"
    
    admin_message = await bot.send_document(
        chat_id=ADMIN_ID,
        document=message.document.file_id,
        caption=admin_text,
        parse_mode="Markdown"
    )
    
    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )
    
    logger.info(f"Переслан документ от {user.username}")

# Обработчик ВИДЕО
@dp.message(F.content_type == ContentType.VIDEO, F.from_user.id != ADMIN_ID)
async def handle_user_video(message: Message):
    user = message.from_user
    
    admin_text = f"{format_user_info(user, message.chat.id)}\n\n"
    admin_text += f"🎥 *Видео*"
    if message.caption:
        admin_text += f"\n📝 *Подпись:* {message.caption}"
    
    admin_message = await bot.send_video(
        chat_id=ADMIN_ID,
        video=message.video.file_id,
        caption=admin_text,
        parse_mode="Markdown"
    )
    
    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )
    
    logger.info(f"Переслано видео от {user.username}")

# Обработчик ОТВЕТОВ АДМИНА (реплаев)
@dp.message(F.from_user.id == ADMIN_ID, F.reply_to_message)
async def handle_admin_reply(message: Message):
    reply_to_id = message.reply_to_message.message_id
    
    # Ищем оригинальное сообщение
    original = get_user_by_admin_message(reply_to_id)
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
        
        # Подтверждение админу
        await message.reply(f"✅ Ответ отправлен пользователю @{username}")
        logger.info(f"Ответ отправлен пользователю {username}")
        
    except Exception as e:
        await message.reply(f"❌ Ошибка при отправке: {e}")
        logger.error(f"Ошибка отправки: {e}")

# Запуск бота
async def main():
    init_db()
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())