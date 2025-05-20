# FiFam v3.2

Telegram-бот для учёта доходов, расходов и анализа чеков.

## 🚀 Запуск

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Создайте `.env` на основе `.env.example` и укажите токен Telegram-бота, DSN базы, ключ OpenAI.

3. Запустите бота:

```bash
python main.py
```

## 🔧 Стек

- aiogram 3.x
- asyncpg
- PostgreSQL
- OpenAI GPT-4 Turbo
- Google Vision OCR

## 🛡️ Ограничения

- Поддержка форматов: JPG, PNG, PDF
- Максимальный размер файла: 5MB
- Безопасное удаление временных файлов
