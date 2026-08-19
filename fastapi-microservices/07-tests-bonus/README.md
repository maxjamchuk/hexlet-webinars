# Стадия 07: Тесты (бонус)

## Что изучаем

Проверяем HTTP-контракт через `pytest` и FastAPI `TestClient`, не затрагивая рабочую базу.

## Что изменилось

По сравнению с `06-docker-final` добавлены пять коротких тестов и override зависимости `get_session`. Каждому тесту достаётся отдельная временная SQLite-база.

## Установка и запуск

```bash
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

Тесты:

```bash
uv run pytest -v
```

Финальный Docker-запуск также сохранён:

```bash
docker compose up --build
```

## Что проверить

Убедитесь, что тесты проверяют `201`, `204`, `404` и `422`, а рядом с проектом не появляется тестовая база.

| Метод и путь | Назначение |
| --- | --- |
| `GET /`, `GET /health` | Информация и проверка состояния |
| `POST /incidents` | Создать запись |
| `GET /incidents` | Список и фильтры |
| `GET /incidents/{incident_id}` | Получить запись |
| `PATCH /incidents/{incident_id}` | Частично обновить запись |
| `DELETE /incidents/{incident_id}` | Удалить запись |

## Мини-задание

Добавьте тест фильтра `GET /incidents?category=creature`. Эта стадия — резервная часть: её можно пропустить, если основное время вебинара закончилось.
