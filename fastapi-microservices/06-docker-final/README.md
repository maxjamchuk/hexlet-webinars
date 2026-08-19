# Стадия 06: Финальный сервис в Docker

## Что изучаем

Упаковываем готовый сервис в воспроизводимый контейнер. Docker здесь — способ одинаково запустить приложение, а не отдельная большая тема.

## Что изменилось

По сравнению с `05-alembic` добавлены Dockerfile, Compose, volume и healthcheck. При старте контейнер сначала выполняет `alembic upgrade head`, затем запускает API. `DATABASE_URL` указывает на SQLite-файл в volume.

## Запуск

```bash
docker compose up --build
```

Локальный запуск без Docker также доступен:

```bash
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

## Что проверить

Откройте [http://localhost:8000/docs](http://localhost:8000/docs) и [http://localhost:8000/health](http://localhost:8000/health). Создайте запись, перезапустите Compose и убедитесь, что volume сохранил данные.

| Метод и путь | Назначение |
| --- | --- |
| `GET /`, `GET /health` | Информация и healthcheck |
| `POST /incidents` | Создать запись |
| `GET /incidents` | Список и фильтры `status`, `category`, `danger_level` |
| `GET /incidents/{incident_id}` | Получить запись |
| `PATCH /incidents/{incident_id}` | Частично обновить запись |
| `DELETE /incidents/{incident_id}` | Удалить запись |

Остановка без удаления данных:

```bash
docker compose down
```

## Мини-задание

Объясните, почему обычный `docker compose down` не удаляет происшествия. [Бонусная стадия](../07-tests-bonus/) добавляет тесты и остаётся резервом вебинара.
