# Task Service

Небольшой учебный Task CRUD API на Flask. Задачи хранятся в
`data/tasks.json`.

Архитектура приложения:

```text
HTTP routes → TaskService → TaskRepository → JSON
                         ↘ NotificationClient → HTTP
```

`NotificationClient` — необязательная внешняя зависимость. При переходе задачи
из незавершённого состояния в завершённое сервис пытается отправить уведомление.
По умолчанию клиент не настроен, поэтому приложение остаётся полностью
автономным. Он добавлен как учебный пример для dependency injection и
тестирования HTTP-зависимостей.

## Требования

- Python 3.12+ для локального запуска
- Docker с Compose для запуска в контейнере

## Запуск

### Вариант 1 — без Docker

```bash
python -m venv .venv
```

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
python -m pip install -e .
python -m flask --app app run --debug
```

API будет доступно по адресу `http://127.0.0.1:5000`.

### Вариант 2 — Docker

```bash
docker compose up --build
```

После запуска список задач доступен по адресу:
`http://localhost:5000/tasks`.

## Примеры запросов

```bash
curl http://localhost:5000/tasks

curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn mocks"}'

curl -X PATCH http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

curl -X DELETE http://localhost:5000/tasks/1
```

## Tests

Без Docker:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m pytest --cov=app
```

С Docker:

```bash
docker compose run --rm app python -m pytest
```

Тесты работают с временными копиями JSON-файла и не изменяют
`data/tasks.json`.
