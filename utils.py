from datetime import datetime
from database import get_user

def format_user_info(user_id, chat_id):
    user = get_user(user_id)
    if not user:
        return f"👤 Пользователь не зарегистрирован\n💬 Chat ID: {chat_id}"

    verified_status = "✅ ПОДТВЕРЖДЕН" if user[7] else "❌ НЕ ПОДТВЕРЖДЕН"
    
    # Форматируем дату рождения в DD.MM.YYYY
    birth_date = datetime.strptime(user[5], "%Y-%m-%d").strftime("%d.%m.%Y")
    
    user_info = (f"👤 От: {user[2] or ''} {user[3] or ''}\n"
                 f"📛 @{user[1] or 'нет'}\n"
                 f"🆔 ID: {user[0]}\n"
                 f"💬 Chat ID: {chat_id}\n"
                 f"🚻 Пол: {user[4]}\n"
                 f"🎂 Дата рождения: {birth_date}\n"
                 f"🛡️ Верификация: {verified_status}")
    
    return user_info

def calculate_age(birth_date_str):
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return None