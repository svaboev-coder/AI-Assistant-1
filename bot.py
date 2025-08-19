import os
import logging
from dotenv import load_dotenv
import telebot
from openai import OpenAI

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и OpenAI клиента
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Системное сообщение для ChatGPT
SYSTEM_MESSAGE = "Ты вежливый и профессиональный личный помощник, работающий в Telegram."

def get_chatgpt_response(user_message):
    """
    Отправляет сообщение пользователя в OpenAI ChatGPT и возвращает ответ
    
    Args:
        user_message (str): Сообщение от пользователя
        
    Returns:
        str: Ответ от ChatGPT или сообщение об ошибке
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Ошибка OpenAI API: {e}")
        return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Обработчик команд /start и /help"""
    welcome_text = """
👋 Привет! Я ваш персональный помощник-секретарь.

Я готов помочь вам с любыми вопросами и задачами. Просто напишите мне сообщение, и я постараюсь быть полезным!

💡 Что я умею:
• Отвечать на вопросы
• Помогать с планированием
• Давать советы и рекомендации
• Общаться на различные темы

Начните наш диалог прямо сейчас! 😊
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    """Обработчик всех текстовых сообщений"""
    try:
        # Показываем, что бот печатает
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Получаем ответ от ChatGPT
        response = get_chatgpt_response(message.text)
        
        # Отправляем ответ пользователю
        bot.reply_to(message, response)
        
        logger.info(f"Обработано сообщение от пользователя {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        bot.reply_to(message, "Извините, произошла ошибка. Попробуйте еще раз.")

def main():
    """Основная функция запуска бота"""
    logger.info("Запуск Telegram-бота...")
    
    # Проверяем наличие токенов
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        logger.error("Не найден TELEGRAM_BOT_TOKEN в переменных окружения!")
        return
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("Не найден OPENAI_API_KEY в переменных окружения!")
        return
    
    logger.info("Бот успешно запущен!")
    
    try:
        # Удаляем webhook перед запуском polling
        bot.delete_webhook()
        logger.info("Webhook удален, запускаем polling...")
        
        # Запускаем бота
        bot.polling(none_stop=True, interval=0)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")

if __name__ == "__main__":
    main()
