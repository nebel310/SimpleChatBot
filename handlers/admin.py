from aiogram import types
from aiogram.filters import Command
from database import ban_user, unban_user, get_user, update_user_verification
from config import ADMIN_ID

async def cmd_ban(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split()[1])
        ban_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} заблокирован.")
    except (IndexError, ValueError):
        await message.answer("❌ Использование: /ban <ID_пользователя>")

async def cmd_unban(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split()[1])
        unban_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} разблокирован.")
    except (IndexError, ValueError):
        await message.answer("❌ Использование: /unban <ID_пользователя>")

async def handle_verification_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        command_parts = message.text.split('_')
        if len(command_parts) != 2:
            await message.answer("❌ Неверный формат команды")
            return
            
        command_type = command_parts[0]
        user_id = int(command_parts[1])
        
        user = get_user(user_id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
            
        if command_type == "/ver":
            update_user_verification(user_id, True)
            await message.bot.send_message(
                user_id,
                "🎉 *Верификация пройдена!*\n\n"
                "Теперь у тебя есть **РЕСПЕКТ** от бота! Ты подтвержденный крутой чел! 🔥\n"
                "Продолжай общаться, теперь ты в особом списке!\n\n"
                "P.S. Если пожелаешь боту здоровья - получишь двойной респект! 😉"
            )
            await message.answer(f"✅ Верификация подтверждена для пользователя {user_id}!")
            
        elif command_type == "/dver":
            update_user_verification(user_id, False)
            await message.bot.send_message(
                user_id,
                "❌ *Верификация не пройдена*\n\n"
                "Эй, ничего страшного! Попробуй еще раз, может быть, нужно быть повнимательнее?\n"
                "Или просто продолжай общаться без респекта - я все равно крутой бот! 😎"
            )
            await message.answer(f"❌ Верификация отклонена для пользователя {user_id}")
        else:
            await message.answer("❌ Неизвестная команда")
            
    except (IndexError, ValueError):
        await message.answer("❌ Неверный формат команды")

async def cmd_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    await message.answer("📊 Админ-панель доступна. Используй /ban и /unban")