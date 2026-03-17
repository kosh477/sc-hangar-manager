# sc-hangar-manager

Базовый каркас сервиса на Flask + SQLAlchemy для работы с MySQL 8.

## Структура

- `app/main.py` — точка входа и создание Flask-приложения.
- `app/config.py` — загрузка параметров окружения и SQLAlchemy URI.
- `app/db.py` — инициализация SQLAlchemy.
- `app/models/` — пакет ORM-моделей.
- `app/routes/` — HTTP-эндпоинты (в т.ч. `/health`).
- `app/templates/` и `app/static/` — каталоги для SSR/статических файлов.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app.main run --host=0.0.0.0 --port=8000
```

Проверка health-check:

```bash
curl http://127.0.0.1:8000/health
```
