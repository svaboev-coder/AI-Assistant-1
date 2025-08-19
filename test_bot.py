import os
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем переменные окружения
load_dotenv()

def test_openai_connection():
    """Тестирует подключение к OpenAI через прокси"""
    try:
        # Проверяем наличие токенов
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        print("🔍 Проверка токенов:")
        print(f"Telegram токен: {'✅ Найден' if telegram_token else '❌ Не найден'}")
        print(f"OpenAI токен: {'✅ Найден' if openai_key else '❌ Не найден'}")
        
        if not openai_key:
            print("\n❌ Ошибка: Не найден OPENAI_API_KEY в переменных окружения!")
            print("Создайте файл .env и добавьте ваш API ключ")
            return False
        
        # Тестируем подключение к OpenAI
        print("\n🤖 Тестирование подключения к OpenAI...")
        client = OpenAI(
            api_key=openai_key,
            base_url="https://api.proxyapi.ru/openai/v1",
        )
        
        # Простой тестовый запрос
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты вежливый помощник."},
                {"role": "user", "content": "Привет! Как дела?"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        print("✅ Подключение к OpenAI успешно!")
        print(f"📝 Ответ: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Тестирование Telegram-бота")
    print("=" * 40)
    
    success = test_openai_connection()
    
    if success:
        print("\n🎉 Все тесты пройдены! Бот готов к запуску.")
        print("Запустите: python bot.py")
    else:
        print("\n⚠️  Обнаружены проблемы. Проверьте настройки.")








