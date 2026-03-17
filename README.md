# sc-hangar-manager

Базовый сервис на Flask + SQLAlchemy для работы с MySQL 8.

## Структура

- `app/main.py` — точка входа и создание Flask-приложения.
- `app/config.py` — загрузка параметров окружения и SQLAlchemy URI.
- `app/db.py` — инициализация SQLAlchemy.
- `app/models/` — пакет ORM-моделей.
- `app/routes/` — API и SSR-эндпоинты.
- `app/templates/` — HTML-страницы для просмотра данных ангара.
- `scripts/start.sh` — запуск контейнера приложения: ожидание БД, миграции, сидирование.
- `scripts/init.sql` — idempotent seed-данные для локального окружения.

## Быстрый запуск в Docker

```bash
docker compose up --build
```

После старта:

- API доступен на `http://localhost:8000`.
- MySQL доступен на `localhost:3306`.

Что происходит при запуске `app` контейнера:

1. устанавливаются зависимости из `requirements.txt`;
2. выполняется ожидание готовности MySQL;
3. применяются миграции `alembic upgrade head`;
4. накатываются seed-данные из `scripts/init.sql`;
5. стартует Flask приложение.

## Миграции

### Применить миграции вручную

```bash
docker compose exec app alembic upgrade head
```

### Откатить последнюю миграцию

```bash
docker compose exec app alembic downgrade -1
```

## Seed-данные

`scripts/init.sql` добавляет:

- 1 пользователя,
- 2 корабля,
- 3 типа компонентов,
- 5 компонентов,
- связи в `shipsByUser`, `partsByUser`, `partsByShip`.

Скрипт использует `ON DUPLICATE KEY UPDATE`, поэтому его можно запускать повторно без создания дублей.

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

### Примеры запросов

Проверка health:

```bash
curl http://127.0.0.1:8000/health
```

Получить список пользователей (должен вернуться seed user):

```bash
curl http://127.0.0.1:8000/users
```

Получить список кораблей:

```bash
curl http://127.0.0.1:8000/ships
```

Получить компоненты пользователя `id=1`:

```bash
curl http://127.0.0.1:8000/user/1/parts
```

Добавить новый тип компонента:

```bash
curl -X POST http://127.0.0.1:8000/part-types \
  -H 'Content-Type: application/json' \
  -d '{"type":"Quantum Drive","isReplaceble":true}'
```

## UI страницы

- `/` — простой фронтенд с авторизацией и кнопками для загрузки данных из API.
- `/ui/user/<id>/ships` — список кораблей пользователя.
- `/ui/user/<id>/parts` — список компонентов пользователя с фильтрами `class`, `size`, `type`.
- `/ui/ship/<id>` — карточка корабля с установленными компонентами.
- `/ui/parts-catalog` — просмотр справочника компонентов и типов.
