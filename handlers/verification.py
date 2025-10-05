import logging
from aiogram import Bot, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import save_message_link, is_user_banned, update_user_verification, get_user
from utils import format_user_info
from config import ADMIN_ID

logger = logging.getLogger(__name__)

class VerificationStates(StatesGroup):
    waiting_for_video_note = State()

async def start_verification(message: types.Message, state: FSMContext):
    if is_user_banned(message.from_user.id):
        return

    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала заверши регистрацию через /start")
        return

    if user[7]:  # is_verified
        await message.answer("🎉 Ты уже верифицирован и имеешь респект от бота!")
        return

    await message.answer(
        "🔐 Запрос на верификацию\n\n"
        "Чтобы получить респект от бота, отправь мне кружочек с твоим лицом!\n\n"
        "💡 Бонус: Если в кружочке будет и голос - это многократный респект!\n\n"
        "Жду твой кружочек... (отправь видео-сообщение)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(VerificationStates.waiting_for_video_note)

async def handle_verification_video_note(message: types.Message, state: FSMContext, bot: Bot):
    if is_user_banned(message.from_user.id):
        await state.clear()
        return

    user = message.from_user
    user_data = get_user(user.id)
    
    admin_text = f"{format_user_info(user.id, message.chat.id)}\n\n"
    admin_text += f"🔴 ЗАПРОС НА ВЕРИФИКАЦИЮ\n"
    admin_text += f"Пользователь хочет получить 'респект' от бота!\n\n"
    admin_text += f"💡 Информация: Если в кружочке есть голос - это многократный респект!\n\n"
    admin_text += f"Используйте команды:\n/ver_{user.id} - подтвердить верификацию\n/dver_{user.id} - отклонить верификацию"

    # Сначала отправляем текстовое сообщение с информацией
    info_message = await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text
    )

    # Затем отправляем само видео-сообщение
    admin_message = await bot.send_video_note(
        chat_id=ADMIN_ID,
        video_note=message.video_note.file_id
    )

    await state.clear()
    
    # Возвращаем основную клавиатуру
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔐 Получить респект (верификация)")],
            [types.KeyboardButton(text="📞 Просто общаться")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "✅ Кружочек отправлен на верификацию! Ожидай решения.\n\n"
        "А пока можешь продолжать общение с ботом!",
        reply_markup=keyboard
    )
    logger.info(f"Переслан запрос верификации от {user.username}")

async def handle_regular_video_note(message: types.Message, bot: Bot):
    """Обработчик обычных кружочков (не для верификации)"""
    if is_user_banned(message.from_user.id):
        return

    user = message.from_user
    
    admin_text = f"{format_user_info(user.id, message.chat.id)}\n\n"
    admin_text += f"📹 Видео-сообщение (кружочек)"

    admin_message = await bot.send_video_note(
        chat_id=ADMIN_ID,
        video_note=message.video_note.file_id
    )

    save_message_link(
        admin_message_id=admin_message.message_id,
        user_id=user.id,
        user_message_id=message.message_id,
        chat_id=message.chat.id,
        username=user.username or user.first_name
    )

    logger.info(f"Переслан обычный кружочек от {user.username}")