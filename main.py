import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID
from database import init_db
from handlers.start import cmd_start, process_gender, process_birth_date
from handlers.admin import cmd_ban, cmd_unban, cmd_stats, handle_verification_command
from handlers.messages import (
    handle_user_text, handle_user_photo, handle_user_voice, 
    handle_user_document, handle_user_video, handle_user_sticker,
    handle_admin_reply  # Импорт из messages, а не verification
)
from handlers.verification import (
    start_verification, handle_verification_video_note, 
    handle_regular_video_note,  # Убрал handle_admin_reply отсюда
    VerificationStates
)
from handlers.start import Registration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация обработчиков команд
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_ban, Command("ban"))
    dp.message.register(cmd_unban, Command("unban"))
    dp.message.register(cmd_stats, Command("stats"))

    # Регистрация обработчиков верификации по командам
    dp.message.register(handle_verification_command, F.text.startswith(('/ver_', '/dver_')))

    # Регистрация обработчиков кнопок
    dp.message.register(start_verification, F.text == "🔐 Получить респект (верификация)")

    # Регистрация обработчиков регистрации
    dp.message.register(process_gender, Registration.waiting_for_gender)
    dp.message.register(process_birth_date, Registration.waiting_for_birth_date)

    # Регистрация обработчиков верификации
    dp.message.register(handle_verification_video_note, F.content_type == "video_note", VerificationStates.waiting_for_video_note)

    # Регистрация обработчиков сообщений от пользователей
    dp.message.register(handle_user_text, F.content_type == "text", F.from_user.id != ADMIN_ID)
    dp.message.register(handle_user_photo, F.content_type == "photo", F.from_user.id != ADMIN_ID)
    dp.message.register(handle_user_voice, F.content_type == "voice", F.from_user.id != ADMIN_ID)
    dp.message.register(handle_user_document, F.content_type == "document", F.from_user.id != ADMIN_ID)
    dp.message.register(handle_user_video, F.content_type == "video", F.from_user.id != ADMIN_ID)
    dp.message.register(handle_user_sticker, F.content_type == "sticker", F.from_user.id != ADMIN_ID)
    dp.message.register(handle_regular_video_note, F.content_type == "video_note", F.from_user.id != ADMIN_ID)

    # Обработчик ответов админа (для обычных сообщений)
    dp.message.register(handle_admin_reply, F.from_user.id == ADMIN_ID, F.reply_to_message)

    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print("Turning off...")