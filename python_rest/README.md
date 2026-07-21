# Python: REST API

Учебный Movie API для воркшопа Hexlet. Приложение использует FastAPI и
SQLite, а исходные 1000 фильмов загружает из `data/movies.json` при создании
пустой базы.

Последовательные примеры работы с API через curl и Python requests находятся
в [examples/README.md](examples/README.md).

## Запуск через Docker Compose

Из каталога `python_rest/` выполните:

```bash
docker compose up --build
```

После запуска доступны:

- Movie API: <http://localhost:8080/movies>
- Swagger UI: <http://localhost:8080/docs>

Compose публикует порт хоста `8080` на внутренний порт контейнера `8000`.

Внешний порт можно изменить через переменную `API_PORT`, например:

```bash
API_PORT=9090 docker compose up --build
```

Для остановки контейнера без удаления данных:

```bash
docker compose down
```

Обычный повторный запуск использует ту же SQLite-базу:

```bash
docker compose up
```

Изменяемая база хранится в named volume, смонтированном в
`/app/runtime`. Seed находится отдельно, внутри image, по пути
`/app/data/movies.json`.

Для полного сброса SQLite и повторной загрузки исходных 1000 фильмов:

```bash
docker compose down -v
docker compose up --build
```

> `docker compose down -v` безвозвратно удаляет фильмы и изменения,
> созданные пользователем в SQLite.

## Локальный запуск без Docker

```bash
uv run --with-requirements requirements.txt \
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

При прямом запуске Uvicorn используется порт из команды. В Docker Compose
приложение продолжает слушать внутренний порт `8000`, а с хоста доступно на
`8080`.

Пути можно переопределить переменными `DATABASE_URL` и
`MOVIES_SEED_PATH`.

## Тесты

```bash
uv run --with-requirements requirements.txt \
  python -m unittest discover -s tests -v
```
