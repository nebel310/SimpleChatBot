from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import random
import logging

from config import BOT_TOKEN
from llm_client import llm_client
from user_profiles import get_user_profile, update_user_profile, increment_message_count

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для машины состояний (FSM)
class ProfileStates(StatesGroup):
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_companion_gender = State()
    waiting_for_companion_age = State()
    waiting_for_name = State()

# Запасные ответы (если API не работает)
FALLBACK_ANSWERS = [
    "Чё каво? Я сейчас туплю...",
    "Ась? Не понял, повтори",
    "Занят, мемы смотрю, потом отвечу",
    "Ты про что? Объясни нормально",
    "Мог бы быть как Илон Маск, но лень",
    "Гонишь))",
    "Сам такой!",
    "Напиши потом, а? А то я занят",
    "Чёт скучно... Расскажи что-нибудь смешное",
    "Я бот, а ты кто? Напомни",
    "Серьёзно? О_о",
    "Ну ты ваще...",
    "Ахах, хорош!",
    "И чо дальше?",
    "Мне похуй если честно",
    "Норм тема, продолжай",
    "Бро, я в ахуе...",
    "Это ты так ко мне подкатываешь?",
    "Погоди, я чипсы доем",
    "Опять ты со своим диалогом..."
]

# Функции для создания клавиатур
def get_gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👦 Мальчик"), KeyboardButton(text="👧 Девочка")],
            [KeyboardButton(text="🤷 Другое")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_companion_gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👦 Хочу общаться с мальчиком"), KeyboardButton(text="👧 Хочу общаться с девочкой")],
            [KeyboardButton(text="🤷 Не важно")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_age_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="13-17"), KeyboardButton(text="18-25")],
            [KeyboardButton(text="26-35"), KeyboardButton(text="36+")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_companion_age_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ровесник(ца)"), KeyboardButton(text="Чуть старше")],
            [KeyboardButton(text="Чуть младше"), KeyboardButton(text="Не важно")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💬 Поболтать"), KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )

# Команды бота
@dp.message(Command("start"))
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    user_name = message.from_user.first_name or "друг"
    
    await message.answer(
        f"👋 Привет, {user_name}!\n\n"
        f"Я бот с характером для живого общения 🎭\n"
        f"Давай настроим твой профиль, чтобы мне было проще с тобой общаться:",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(ProfileStates.waiting_for_gender)

@dp.message(Command("help"))
async def help_cmd(message: Message):
    help_text = """
🤖 <b>Помощь по боту</b>

<b>Основные команды:</b>
/start - начать настройку профиля
/settings - изменить настройки профиля  
/profile - посмотреть свой профиль
/help - показать эту справку

<b>Как работает бот:</b>
• Я использую ИИ для генерации ответов
• Подстраиваюсь под твой стиль общения
• Могу быть немного грубым (по-дружески)
• Стараюсь поддерживать любые темы

<b>Кнопки:</b>
💬 Поболтать - начать общение
⚙️ Настройки - изменить профиль
👤 Мой профиль - посмотреть настройки

Если бот не отвечает - возможно, закончились бесплатные запросы к API.
    """
    await message.answer(help_text, reply_markup=get_main_keyboard())

@dp.message(Command("settings"))
async def settings_cmd(message: Message, state: FSMContext):
    await message.answer(
        "⚙️ <b>Настройки профиля</b>\n\n"
        "Давай обновим твои данные. Для начала выбери свой пол:",
        reply_markup=get_gender_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_gender)

@dp.message(Command("profile"))
async def profile_cmd(message: Message):
    profile = get_user_profile(message.from_user.id)
    
    # Красивое описание настроек
    gender_emoji = "👦" if profile['user_gender'] == "мальчик" else "👧" if profile['user_gender'] == "девочка" else "🤷"
    companion_emoji = "👦" if profile['companion_gender'] == "мальчик" else "👧" if profile['companion_gender'] == "девочка" else "🤷"
    
    profile_text = f"""
👤 <b>Твой профиль</b>

{gender_emoji} <b>Ты:</b> {profile['user_gender']}, {profile['user_age']}
📛 <b>Имя:</b> {profile['user_name']}
{companion_emoji} <b>Собеседник:</b> {profile['companion_gender']}, {profile['companion_age']}
💬 <b>Сообщений:</b> {profile.get('messages_count', 0)}

Изменить настройки: /settings
    """
    await message.answer(profile_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

# Обработчики кнопок
@dp.message(F.text == "ℹ️ Помощь")
async def help_button(message: Message):
    await help_cmd(message)

@dp.message(F.text == "⚙️ Настройки")
async def settings_button(message: Message, state: FSMContext):
    await settings_cmd(message, state)

@dp.message(F.text == "👤 Мой профиль")
async def profile_button(message: Message):
    await profile_cmd(message)

@dp.message(F.text == "💬 Поболтать")
async def chat_button(message: Message):
    profile = get_user_profile(message.from_user.id)
    if profile['user_gender'] == 'не указано':
        await message.answer("Сначала настрой профиль! Напиши /start")
        return
        
    await message.answer(
        f"Отлично, {profile['user_name']}! 💬\n"
        f"Просто напиши что-нибудь - отвечу как {profile['companion_gender']} {profile['companion_age']} лет!",
        reply_markup=ReplyKeyboardRemove()
    )

# Обработчики состояний настройки профиля
@dp.message(ProfileStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    gender_map = {
        "👦 Мальчик": "мальчик",
        "👧 Девочка": "девочка", 
        "🤷 Другое": "не указано"
    }
    
    gender = gender_map.get(message.text, "не указано")
    update_user_profile(message.from_user.id, user_gender=gender)
    
    await message.answer("Сколько тебе лет?", reply_markup=get_age_keyboard())
    await state.set_state(ProfileStates.waiting_for_age)

@dp.message(ProfileStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    if message.text not in ["13-17", "18-25", "26-35", "36+"]:
        await message.answer("Пожалуйста, выбери возраст из кнопок ниже:", reply_markup=get_age_keyboard())
        return
        
    update_user_profile(message.from_user.id, user_age=message.text)
    
    await message.answer("С кем хочешь пообщаться?", reply_markup=get_companion_gender_keyboard())
    await state.set_state(ProfileStates.waiting_for_companion_gender)

@dp.message(ProfileStates.waiting_for_companion_gender)
async def process_companion_gender(message: Message, state: FSMContext):
    gender_map = {
        "👦 Хочу общаться с мальчиком": "мальчик",
        "👧 Хочу общаться с девочкой": "девочка",
        "🤷 Не важно": "не важно"
    }
    
    companion_gender = gender_map.get(message.text, "не важно")
    update_user_profile(message.from_user.id, companion_gender=companion_gender)
    
    await message.answer("Какого возраста собеседник?", reply_markup=get_companion_age_keyboard())
    await state.set_state(ProfileStates.waiting_for_companion_age)

@dp.message(ProfileStates.waiting_for_companion_age)
async def process_companion_age(message: Message, state: FSMContext):
    age_map = {
        "Ровесник(ца)": "ровесник",
        "Чуть старше": "чуть старше",
        "Чуть младше": "чуть младше", 
        "Не важно": "не важно"
    }
    
    companion_age = age_map.get(message.text, "не важно")
    update_user_profile(message.from_user.id, companion_age=companion_age)
    
    await message.answer(
        "Как тебя зовут? (или как хочешь, чтобы к тебе обращались)\n\n"
        "<i>Можно написать любое имя или прозвище</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ProfileStates.waiting_for_name)

@dp.message(ProfileStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    user_name = message.text.strip() if message.text.strip() else "друг"
    update_user_profile(message.from_user.id, user_name=user_name)
    
    profile = get_user_profile(message.from_user.id)
    
    await message.answer(
        f"🎉 <b>Отлично, {user_name}!</b>\n\n"
        f"Профиль настроен!\n"
        f"Теперь я буду общаться с тобой как <b>{profile['companion_gender']} {profile['companion_age']}</b> лет.\n\n"
        f"Просто напиши что-нибудь для начала разговора! ✨",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()

# Основной обработчик сообщений
@dp.message()
async def ai_reply(message: Message):
    # Игнорируем команды и слишком длинные сообщения
    if message.text.startswith('/') or len(message.text) > 500:
        return
        
    # Проверяем, есть ли настройки профиля
    profile = get_user_profile(message.from_user.id)
    if profile['user_gender'] == 'не указано':
        await message.answer(
            "🤔 Сначала давай настроим твой профиль!\n"
            "Напиши /start чтобы начать настройку",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Увеличиваем счетчик сообщений
    increment_message_count(message.from_user.id)
    
    # Случайная задержка для естественности (1-5 секунд)
    delay = random.uniform(1, 5)
    await asyncio.sleep(delay)
    
    # Показываем действие "печатает"
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Получаем ответ от LLM
    ai_response = await llm_client.get_response(message.from_user.id, message.text)
    
    # Если API вернуло ошибку, используем запасные ответы
    if any(ai_response.startswith(prefix) for prefix in ['❌', '⚠️', '⚠', 'Ошибка']):
        logger.warning(f"API Error for user {message.from_user.id}: {ai_response}")
        ai_response = random.choice(FALLBACK_ANSWERS)
    
    # Добавляем небольшую случайную задержку перед отправкой
    await asyncio.sleep(random.uniform(0.5, 2))
    await message.answer(ai_response, reply_markup=get_main_keyboard())

# Обработчик ошибок
@dp.errors()
async def errors_handler(update, exception):
    logger.error(f"Ошибка: {exception}", exc_info=True)
    
# Запуск бота
async def main():
    logger.info("Запускаю бота...")
    
    # Проверяем наличие токена
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден! Проверь .env файл")
        return
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())