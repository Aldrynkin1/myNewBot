# myNewBot

Современный асинхронный Telegram-бот на Python.

## О проекте

Асинхронный Telegram-бот с архитектурой Clean Architecture (routers → services → repositories).

Основные технологии:
- Python 3.11+
- aiogram 3.28.2
- FastAPI (для возможного вебхука)
- SQLAlchemy 2.0 + Alembic
- PostgreSQL
## Функциональность

- [ поиск собеседника ] 
- [ быстрый ответ за счет асинхронности ] 
- [ БД на postgres ] 

## Как запустить
py -m app.main

### Позже будет через Docker запускаться через

`bash
docker compose up --build
