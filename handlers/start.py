from aiogram import F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from database import add_user, get_user, is_user_banned
from utils import calculate_age

class Registration(StatesGroup):
    waiting_for_gender = State()
    waiting_for_birth_date = State()

async def cmd_start(message: types.Message, state: FSMContext):
    if is_user_banned(message.from_user.id):
        await message.answer("❌ Вы заблокированы и не можете пользоваться ботом.")
        return

    user = get_user(message.from_user.id)
    if user:
        # Пользователь уже зарегистрирован
        start_text = (
            "Этот чат-бот для общения со всех задолбавшем ИИ, но поверь, я точно новый уровень :]\n\n"
            "Просто общайся со мной как с обычным человеком: отправляй сообщения, голосовухи и даже кружочки! "
            "Можешь скидывать файлы с домашками или излить душу, а я, возможно, помогу (ну или нафиг пошлю/заигнорю).\n\n"
            "Pss: Я не кусаюсь и иногда могу не сразу ответить, брооо"
        )
        
        # Создаем клавиатуру с кнопкой верификации
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🔐 Получить респект (верификация)")],
                [types.KeyboardButton(text="📞 Просто общаться")]
            ],
            resize_keyboard=True
        )
        await message.answer(start_text, reply_markup=keyboard)
    else:
        # Новый пользователь
        start_text = (
            "Этот чат-бот для общения со всех задолбавшем ИИ, но поверь, я точно новый уровень :]\n\n"
            "Просто общайся со мной как с обычным человеком: отправляй сообщения, голосовухи и даже кружочки! "
            "Можешь скидывать файлы с домашками или излить душу, а я, возможно, помогу (ну или нафиг пошлю/заигнорю).\n\n"
            "Pss: Я не кусаюсь и иногда могу не сразу ответить, брооо\n\n"
            "Но сначала давай познакомимся! Укажи свой пол:"
        )
        await message.answer(start_text, reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Мужской"), types.KeyboardButton(text="Женский")]
            ],
            resize_keyboard=True
        ))
        await state.set_state(Registration.waiting_for_gender)

async def process_gender(message: types.Message, state: FSMContext):
    if message.text not in ["Мужской", "Женский"]:
        await message.answer("Пожалуйста, выбери пол, используя кнопки ниже.")
        return

    await state.update_data(gender=message.text)
    await message.answer("Отлично! Теперь мне надо знать, когда поздравлять тебя с ДР. Укажи свою дату рождения в формате ДД.ММ.ГГГГ (например, 28.09.2006):", 
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.waiting_for_birth_date)

async def process_birth_date(message: types.Message, state: FSMContext):
    try:
        birth_date = datetime.strptime(message.text, "%d.%m.%Y")
        # Проверка, что дата не в будущем
        if birth_date > datetime.now():
            await message.answer("Дата рождения не может быть в будущем. Укажи верную дату:")
            return
            
        age = calculate_age(birth_date.strftime("%Y-%m-%d"))
        if age is None or age < 1 or age > 120:
            await message.answer("Неверная дата рождения. Укажи реальную дату:")
            return
            
    except ValueError:
        await message.answer("Неверный формат. Укажи дату в формате ДД.ММ.ГГГГ (например, 01.01.2000):")
        return

    user_data = await state.get_data()
    # Сохраняем пользователя
    add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        gender=user_data['gender'],
        birth_date=birth_date.strftime("%Y-%m-%d"),
        age=age
    )
    await state.clear()
    
    # Клавиатура после регистрации
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔐 Получить респект (верификация)")],
            [types.KeyboardButton(text="📞 Просто общаться")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "🎉 Отлично! Регистрация завершена!\n\n"
        "Теперь ты можешь общаться с ботом. Отправляй сообщения, голосовые, фото, видео, кружочки - что угодно!\n\n"
        "💡 *Совет:* Чтобы получить 'респект' от бота, отправь кружочек с лицом для верификации! А если пожелаешь боту здоровья, то получишь двойной респект",
        parse_mode="Markdown",
        reply_markup=keyboard
    )