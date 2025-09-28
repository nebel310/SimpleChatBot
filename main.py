import os
import requests
from flask import Flask, request, jsonify, render_template
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

app = Flask(__name__)

# Конфиг
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL') + '/webhook'

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)

# Обработчики сообщений
def start(update, context):
    update.message.reply_text('Привет! Я бот для общения 😊 Напиши что-нибудь!')

def handle_message(update, context):
    user_message = update.message.text
    user_name = update.message.from_user.first_name
    
    # Простые ответы
    responses = [
        f"Привет, {user_name}! Крутое сообщение: {user_message}",
        "Хм, интересно... А расскажи подробнее!",
        "Я пока простой бот, но я рад с тобой общаться!",
        "😊 Забавно! Продолжай в том же духе!",
        f"{user_name}, ты сегодня в ударе! Мне нравится!"
    ]
    
    # Случайный ответ
    import random
    response = random.choice(responses)
    update.message.reply_text(response)

# Веб-интерфейс
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Чат-бот</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0; padding: 20px; min-height: 100vh;
            }
            .chat-container {
                max-width: 400px; margin: 0 auto;
                background: white; border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .chat-header {
                background: #4CAF50; color: white;
                padding: 20px; text-align: center;
                font-size: 24px; font-weight: bold;
            }
            .chat-content {
                padding: 20px; min-height: 300px;
            }
            .message { margin: 15px 0; }
            .user-message { text-align: right; color: #333; }
            .bot-message { text-align: left; color: #666; }
            .input-area {
                display: flex; padding: 20px;
                background: #f5f5f5;
            }
            input {
                flex: 1; padding: 12px; border: none;
                border-radius: 25px; margin-right: 10px;
            }
            button {
                background: #4CAF50; color: white;
                border: none; padding: 12px 20px;
                border-radius: 25px; cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">💬 Чат с ботом</div>
            <div class="chat-content" id="chat">
                <div class="message bot-message">
                    Привет! Напиши мне что-нибудь! 😊
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="userInput" placeholder="Введите сообщение...">
                <button onclick="sendMessage()">Отправить</button>
            </div>
        </div>

        <script>
            function sendMessage() {
                const input = document.getElementById('userInput');
                const message = input.value.trim();
                
                if (message) {
                    // Добавляем сообщение пользователя
                    const chat = document.getElementById('chat');
                    chat.innerHTML += `<div class="message user-message">${message}</div>`;
                    
                    // Симуляция ответа бота
                    setTimeout(() => {
                        const responses = [
                            "Интересно! Расскажи еще что-нибудь!",
                            "Хм, я подумаю над этим... 🤔",
                            "Классно! А что еще тебя интересует?",
                            "Продолжаем беседу! Что на уме?",
                            "Забавно! У тебя есть чувство юмора! 😄"
                        ];
                        const response = responses[Math.floor(Math.random() * responses.length)];
                        chat.innerHTML += `<div class="message bot-message">${response}</div>`;
                        chat.scrollTop = chat.scrollHeight;
                    }, 1000);
                    
                    input.value = '';
                    chat.scrollTop = chat.scrollHeight;
                }
            }
            
            // Отправка по Enter
            document.getElementById('userInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """

# Вебхук для Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(), bot)
        dispatcher = Dispatcher(bot, None, workers=0)
        
        # Регистрируем обработчики
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        dispatcher.process_update(update)
    return 'ok'

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    s = bot.set_webhook(WEBHOOK_URL)
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)