# Стадия 05: Alembic

## Что изучаем

Управляем схемой SQLite явными, воспроизводимыми миграциями Alembic.

## Что изменилось

По сравнению с `04-sqlite-sqlalchemy` вызов `Base.metadata.create_all()` удалён. Начальная миграция создаёт таблицу `incidents`, а приложение ожидает подготовленную базу. Alembic и приложение читают один `DATABASE_URL`.

## Установка, миграция и запуск

```bash
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

## Что проверить

Удалите локальную учебную базу, снова выполните `uv run alembic upgrade head`, затем откройте `/docs` и создайте запись.

| Метод и путь | Назначение |
| --- | --- |
| `GET /`, `GET /health` | Информация и проверка состояния |
| `POST /incidents` | Создать запись |
| `GET /incidents` | Список и фильтры `status`, `category`, `danger_level` |
| `GET /incidents/{incident_id}` | Получить запись |
| `PATCH /incidents/{incident_id}` | Частично обновить запись |
| `DELETE /incidents/{incident_id}` | Удалить запись |

## Мини-задание

Сравните ORM-модель и начальную миграцию: какие ограничения относятся к HTTP-валидации, а какие — к схеме БД? На [следующей стадии](../06-docker-final/) миграция будет выполняться при старте контейнера.
