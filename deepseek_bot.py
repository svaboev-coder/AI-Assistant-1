import os
import logging
import asyncio
import json
from dotenv import load_dotenv
import aiohttp
from telebot.async_telebot import AsyncTeleBot

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = AsyncTeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# Системное сообщение для DeepSeek
SYSTEM_MESSAGE = "Ты вежливый и профессиональный личный помощник, работающий в Telegram."

async def get_deepseek_response(user_message):
    """
    Отправляет сообщение пользователя в DeepSeek через Chutes API и возвращает ответ
    
    Args:
        user_message (str): Сообщение от пользователя
        
    Returns:
        str: Ответ от DeepSeek или сообщение об ошибке
    """
    try:
        api_token = os.getenv('CHUTES_API_TOKEN')
        if not api_token:
            logger.error("Не найден CHUTES_API_TOKEN в переменных окружения!")
            return "Извините, произошла ошибка конфигурации. Обратитесь к администратору."
        
        headers = {
            "Authorization": "Bearer " + api_token,
            "Content-Type": "application/json"
        }
        
        body = {
            "model": "deepseek-ai/DeepSeek-R1",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "stream": True,
            "max_tokens": 1024,
            "temperature": 0.7
        }

        response_text = ""
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://llm.chutes.ai/v1/chat/completions", 
                headers=headers,
                json=body
            ) as response:
                if response.status != 200:
                    logger.error(f"Ошибка API Chutes: {response.status}")
                    return "Извините, произошла ошибка при обращении к нейросети. Попробуйте позже."
                
                async for line in response.content:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data)
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                choice = chunk_data['choices'][0]
                                if 'delta' in choice and 'content' in choice['delta']:
                                    content = choice['delta']['content']
                                    if content:
                                        response_text += content
                        except json.JSONDecodeError:
                            # Пропускаем невалидные JSON строки
                            continue
                        except Exception as e:
                            logger.error(f"Ошибка при обработке chunk: {e}")
                            continue
        
        if response_text.strip():
            return response_text.strip()
        else:
            return "Извините, не удалось получить ответ. Попробуйте переформулировать вопрос."
            
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе к Chutes API: {e}")
        return "Извините, произошла ошибка сети. Проверьте подключение к интернету."
    except Exception as e:
        logger.error(f"Неожиданная ошибка в get_deepseek_response: {e}")
        return "Произошла неожиданная ошибка. Попробуйте позже."

@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    """Обработчик команд /start и /help"""
    welcome_text = """
🤖 Привет! Я ваш персональный помощник на базе DeepSeek.

Я готов помочь вам с любыми вопросами и задачами. Просто напишите мне сообщение, и я постараюсь быть полезным!

💡 Что я умею:
• Отвечать на вопросы любой сложности
• Помогать с анализом и планированием
• Давать советы и рекомендации
• Решать творческие и технические задачи
• Общаться на различные темы

✨ Powered by DeepSeek-R1 через Chutes AI

Начните наш диалог прямо сейчас! 😊
    """
    await bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
async def handle_text_message(message):
    """Обработчик всех текстовых сообщений"""
    try:
        # Показываем, что бот печатает
        await bot.send_chat_action(message.chat.id, 'typing')
        
        # Получаем ответ от DeepSeek
        response = await get_deepseek_response(message.text)
        
        # Telegram имеет ограничение на длину сообщения (4096 символов)
        if len(response) > 4000:
            # Разбиваем длинный ответ на части
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await bot.reply_to(message, part)
        else:
            await bot.reply_to(message, response)
        
        logger.info(f"Обработано сообщение от пользователя {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await bot.reply_to(message, "Извините, произошла ошибка. Попробуйте еще раз.")

async def main():
    """Основная асинхронная функция запуска бота"""
    logger.info("Запуск Telegram-бота с DeepSeek...")
    
    # Проверяем наличие токенов
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        logger.error("Не найден TELEGRAM_BOT_TOKEN в переменных окружения!")
        return
    
    if not os.getenv('CHUTES_API_TOKEN'):
        logger.error("Не найден CHUTES_API_TOKEN в переменных окружения!")
        return
    
    logger.info("Бот успешно запущен!")
    
    try:
        # Удаляем webhook перед запуском polling
        await bot.delete_webhook()
        logger.info("Webhook удален, запускаем polling...")
        
        # Запускаем бота
        await bot.polling(none_stop=True, interval=0)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        await bot.close_session()

if __name__ == "__main__":
    asyncio.run(main())







