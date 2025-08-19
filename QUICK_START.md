# 🚀 Быстрый запуск Telegram-бота

## Шаг 1: Установка зависимостей
```bash
pip install -r requirements.txt
```

## Шаг 2: Настройка токенов
1. Скопируйте файл с примерами:
   ```bash
   copy env_example.txt .env
   ```

2. Отредактируйте файл `.env` и добавьте ваши токены:
   ```env
   TELEGRAM_BOT_TOKEN=ваш_токен_бота
   OPENAI_API_KEY=ваш_ключ_proxyapi
   ```

## Шаг 3: Получение токенов

### Telegram Bot Token
1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

### ProxyAPI Key
1. Зарегистрируйтесь на https://api.proxyapi.ru/
2. Получите API ключ
3. Скопируйте ключ

## Шаг 4: Тестирование
```bash
python test_bot.py
```

## Шаг 5: Запуск бота
```bash
python bot.py
```

## ✅ Готово!
Найдите вашего бота в Telegram и отправьте `/start`

---

## 🔧 Устранение проблем

### Ошибка "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Ошибка "Не найден токен"
Проверьте файл `.env` в корне проекта

### Ошибка API
Проверьте баланс на ProxyAPI и правильность ключа








