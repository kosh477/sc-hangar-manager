# sc-hangar-manager

Базовый сервис на Flask + SQLAlchemy для работы с MySQL 8.

## Структура

- `app/main.py` — точка входа и создание Flask-приложения.
- `app/config.py` — загрузка параметров окружения и SQLAlchemy URI.
- `app/db.py` — инициализация SQLAlchemy.
- `app/models/` — пакет ORM-моделей.
- `app/routes/` — API и SSR-эндпоинты.
- `app/templates/` — HTML-страницы для просмотра данных ангара.

## API

Реализованы endpoint'ы:

- `GET/POST /users`
- `GET/POST /ships`
- `GET/POST /parts`
- `GET/POST /part-types`
- `GET/POST /ship/{id}/parts`
- `GET/POST /user/{id}/ships` (soft-delete через `isDeleted=true`)
- `GET/POST /user/{id}/parts` (soft-delete через `isDeleted=true`)

Ошибки API:

- `400` — невалидные входные данные
- `404` — сущность не найдена
- `409` — конфликт/дубликат

## UI страницы

- `/ui/user/<id>/ships` — список кораблей пользователя.
- `/ui/user/<id>/parts` — список компонентов пользователя с фильтрами `class`, `size`, `type`.
- `/ui/ship/<id>` — карточка корабля с установленными компонентами.
- `/ui/parts-catalog` — просмотр справочника компонентов и типов.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app.main run --host=0.0.0.0 --port=8000
```

Проверка health-check:

```bash
curl http://127.0.0.1:8000/health
```

## Миграции (Alembic)

```bash
alembic upgrade head
```
