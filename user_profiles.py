"""
Хранение профилей пользователей в оперативной памяти
Для продакшена лучше использовать базу данных
"""

# Словарь для хранения профилей {user_id: profile_data}
user_profiles = {}

def get_user_profile(user_id):
    """
    Получить профиль пользователя
    Если профиля нет - возвращает настройки по умолчанию
    """
    return user_profiles.get(user_id, {
        'user_gender': 'не указано',
        'user_age': 'не указано',
        'companion_gender': 'не указано', 
        'companion_age': 'не указано',
        'user_name': 'друг',
        'messages_count': 0
    })

def update_user_profile(user_id, **kwargs):
    """
    Обновить профиль пользователя
    """
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            'user_gender': 'не указано',
            'user_age': 'не указано',
            'companion_gender': 'не указано',
            'companion_age': 'не указано',
            'user_name': 'друг',
            'messages_count': 0
        }
    
    # Обновляем переданные поля
    for key, value in kwargs.items():
        if key in user_profiles[user_id]:
            user_profiles[user_id][key] = value
    
    # Увеличиваем счетчик сообщений
    if 'messages_count' in user_profiles[user_id]:
        user_profiles[user_id]['messages_count'] += 1

def increment_message_count(user_id):
    """
    Увеличить счетчик сообщений пользователя
    """
    if user_id in user_profiles:
        user_profiles[user_id]['messages_count'] = user_profiles[user_id].get('messages_count', 0) + 1
    else:
        user_profiles[user_id] = {
            'user_gender': 'не указано',
            'user_age': 'не указано',
            'companion_gender': 'не указано',
            'companion_age': 'не указано',
            'user_name': 'друг',
            'messages_count': 1
        }

def get_all_profiles():
    """
    Получить все профили (для отладки)
    """
    return user_profiles