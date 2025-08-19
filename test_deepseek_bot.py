import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

async def test_chutes_connection():
    """Тестирует подключение к Chutes API"""
    try:
        # Проверяем наличие токенов
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chutes_token = os.getenv('CHUTES_API_TOKEN')
        
        print("🔍 Проверка токенов:")
        print(f"Telegram токен: {'✅ Найден' if telegram_token else '❌ Не найден'}")
        print(f"Chutes токен: {'✅ Найден' if chutes_token else '❌ Не найден'}")
        
        if not chutes_token:
            print("\n❌ Ошибка: Не найден CHUTES_API_TOKEN в переменных окружения!")
            print("Создайте файл .env и добавьте ваш API токен Chutes")
            return False
        
        # Тестируем подключение к Chutes API
        print("\n🤖 Тестирование подключения к DeepSeek через Chutes...")
        
        headers = {
            "Authorization": "Bearer " + chutes_token,
            "Content-Type": "application/json"
        }
        
        body = {
            "model": "deepseek-ai/DeepSeek-R1",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты вежливый и профессиональный личный помощник, работающий в Telegram."
                },
                {
                    "role": "user",
                    "content": "Привет! Как дела?"
                }
            ],
            "stream": True,
            "max_tokens": 100,
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
                    print(f"❌ Ошибка API: {response.status}")
                    error_text = await response.text()
                    print(f"Детали ошибки: {error_text}")
                    return False
                
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
                            continue
                        except Exception as e:
                            print(f"⚠️  Ошибка при обработке chunk: {e}")
                            continue
        
        if response_text.strip():
            print("✅ Подключение к DeepSeek через Chutes успешно!")
            print(f"📝 Ответ: {response_text.strip()}")
            return True
        else:
            print("❌ Не удалось получить ответ от DeepSeek")
            return False
            
    except aiohttp.ClientError as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

async def main():
    print("🧪 Тестирование Telegram-бота с DeepSeek")
    print("=" * 50)
    
    success = await test_chutes_connection()
    
    if success:
        print("\n🎉 Все тесты пройдены! Бот готов к запуску.")
        print("Запустите: python deepseek_bot.py")
    else:
        print("\n⚠️  Обнаружены проблемы. Проверьте настройки.")

if __name__ == "__main__":
    asyncio.run(main())
