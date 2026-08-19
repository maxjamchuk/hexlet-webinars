# Стадия 03: CRUD в памяти

## Что изучаем

Собираем полный CRUD, фильтруем список и реализуем частичное обновление.

## Что изменилось

По сравнению с `02-pydantic` добавлены `IncidentUpdate`, `PATCH`, `DELETE` и фильтры. `PATCH` применяет только переданные поля через `model_dump(exclude_unset=True)`.

## Установка и запуск

```bash
uv sync
uv run fastapi dev app/main.py
```

## Что проверить

Создайте запись в `/docs`, измените только `status`, отфильтруйте список и удалите запись. После перезапуска данные исчезнут.

| Метод и путь | Назначение |
| --- | --- |
| `GET /`, `GET /health` | Информация и проверка состояния |
| `POST /incidents` | Создать запись |
| `GET /incidents` | Список; фильтры `status`, `category`, `danger_level` |
| `GET /incidents/{incident_id}` | Получить запись |
| `PATCH /incidents/{incident_id}` | Частично обновить запись |
| `DELETE /incidents/{incident_id}` | Удалить запись |

## Мини-задание

Объясните, почему данные пропадают при перезапуске. На [следующей стадии](../04-sqlite-sqlalchemy/) их сохранит SQLite.
