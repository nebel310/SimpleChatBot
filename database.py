import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  gender TEXT,
                  birth_date TEXT,
                  age INTEGER,
                  is_verified BOOLEAN DEFAULT FALSE,
                  is_banned BOOLEAN DEFAULT FALSE,
                  registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Таблица связей сообщений
    c.execute('''CREATE TABLE IF NOT EXISTS message_links
                 (admin_message_id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  user_message_id INTEGER,
                  chat_id INTEGER,
                  username TEXT,
                  is_verification BOOLEAN DEFAULT FALSE)''')
    
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id, username, first_name, last_name, gender, birth_date, age):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, gender, birth_date, age) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (user_id, username, first_name, last_name, gender, birth_date, age))
    conn.commit()
    conn.close()

def update_user_verification(user_id, is_verified):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET is_verified=? WHERE user_id=?", (is_verified, user_id))
    conn.commit()
    conn.close()

def ban_user(user_id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def save_message_link(admin_message_id, user_id, user_message_id, chat_id, username, is_verification=False):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO message_links VALUES (?, ?, ?, ?, ?, ?)",
              (admin_message_id, user_id, user_message_id, chat_id, username, is_verification))
    conn.commit()
    conn.close()

def get_user_by_admin_message(admin_message_id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM message_links WHERE admin_message_id=?", (admin_message_id,))
    result = c.fetchone()
    conn.close()
    return result

def is_user_banned(user_id):
    user = get_user(user_id)
    return user and user[8]  # is_banned field