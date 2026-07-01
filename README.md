# Mos.ru Lost Items Demo

Демостенд сервиса поиска потерянных вещей в метро.

Сценарий:

- пользователь описывает потерянную вещь в Telegram-боте;
- выбирает дату и станцию;
- backend создает заявку;
- система ищет похожие вещи в синтетической базе;
- пользователь получает top-3 совпадения или ответ, что совпадений нет;
- для найденной вещи можно проверить скрытый признак.

## Стэк

- Python 3.12
- FastAPI
- aiogram
- PostgreSQL 16
- pgvector
- SQLAlchemy Async
- Alembic
- Docker Compose
- OpenRouter embeddings

## Секреты и конфигурация

Пример переменных находится в:

```text
.env.example
```

Для эмбеддингов нужен:

```text
OPENROUTER_API_KEY=...
```

Для Telegram-бота нужен:

```text
TELEGRAM_BOT_TOKEN=...
```

Если бот запускается внутри Docker Compose, укажите:

```text
BACKEND_API_URL=http://api:8000
```

## Запуск backend и базы

Запустить PostgreSQL + FastAPI:

```powershell
docker compose up --build
```

Backend доступен по адресу:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

Healthcheck:

```powershell
curl http://localhost:8000/health
```

## Миграции

Применить миграции:

```powershell
docker compose exec -w /app api alembic -c alembic.ini upgrade head
```

## Синтетические данные

Заполнить демо-базу:

```powershell
docker compose exec api python scripts/seed_demo_db.py
```

Заполнить embeddings для найденных вещей:

```powershell
docker compose exec api python scripts/fill_embeddings.py
```

## HTTP API

Основные endpoint'ы:

```text
GET  /health
GET  /stations
GET  /demo/found-items
POST /lost-requests
POST /lost-requests/{request_id}/claim-check
```

Синтетическую базу для демонстрации можно посмотреть здесь:

```text
http://localhost:8000/demo/found-items
```

Интерактивная документация API:

```text
http://localhost:8000/docs
```