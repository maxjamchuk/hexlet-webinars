# Python: Продвинутое тестирование — Task Service

Учебный Task CRUD API на Flask для вебинара о продвинутом тестировании Python.
Задачи хранятся в JSON-файле.

Архитектура приложения:

```text
HTTP routes → TaskService → TaskRepository → JSON
                         ↘ NotificationClient → requests
```

`NotificationClient` — необязательная внешняя зависимость. При переходе задачи
из незавершённого состояния в завершённое сервис пытается отправить уведомление.
По умолчанию клиент не настроен, поэтому приложение остаётся автономным.

## Материалы вебинара

- [Презентация](https://docs.google.com/presentation/d/1iYCByyPJx1UUZhTQNTX44bMYZ43HiDCtgjH7Gqkcw2g)
- [Репозиторий проекта](https://github.com/maxjamchuk/hexlet-webinars/tree/main/task-service)

## Что разбирается в проекте

- `pytest.raises` и параметризация;
- pytest fixtures, `tmp_path` и файловые side effects;
- Flask `test_client`;
- dependency injection;
- `Mock`, `assert_called_once_with` и `side_effect`;
- `monkeypatch`;
- тестирование внешнего HTTP-клиента;
- преобразование `RequestException` в `NotificationError`;
- локальный запуск и Docker.

## Структура проекта

```text
task-service/
├── app/
│   ├── __init__.py              # application factory и сборка зависимостей
│   ├── routes.py                # HTTP endpoints
│   ├── service.py               # бизнес-логика и валидация
│   ├── repository.py            # чтение и запись JSON
│   └── notifications.py         # внешний HTTP-клиент
├── data/
│   └── tasks.json               # данные локального приложения
├── tests/
│   ├── fixtures/
│   │   └── tasks.json           # неизменяемые исходные данные тестов
│   ├── conftest.py              # общие pytest fixtures
│   ├── test_service.py
│   ├── test_repository.py
│   ├── test_routes.py
│   └── test_notifications.py
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── pyproject.toml
└── README.md
```

## API

| Метод и путь | Назначение | Успешный статус |
| --- | --- | --- |
| `GET /tasks` | Получить все задачи | `200 OK` |
| `GET /tasks/<id>` | Получить задачу по ID | `200 OK` |
| `POST /tasks` | Создать задачу | `201 Created` |
| `PATCH /tasks/<id>` | Изменить заголовок или статус задачи | `200 OK` |
| `DELETE /tasks/<id>` | Удалить задачу | `204 No Content` |

## Запуск приложения

Требуется Python 3.12+ или Docker с Compose. Все команды выполняются из папки
`task-service`.

### Вариант 1 — без Docker

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активируйте его в Linux или macOS:

```bash
source .venv/bin/activate
```

В Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Установите проект и запустите Flask:

```bash
python -m pip install -e .
python -m flask --app app run --debug
```

API будет доступно по адресу `http://localhost:5000/tasks`.

### Вариант 2 — Docker

```bash
docker compose build
docker compose up
```

API будет доступно по адресу `http://localhost:5000/tasks`.

Для остановки:

```bash
docker compose down
```

## Примеры curl

Команды ниже можно последовательно выполнить после запуска приложения:

```bash
curl http://localhost:5000/tasks
```

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn mocks"}'
```

```bash
curl -X PATCH http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

```bash
curl -X DELETE http://localhost:5000/tasks/1
```

## Тесты

Установите зависимости для разработки:

```bash
python -m pip install -e ".[dev]"
```

Весь набор:

```bash
python -m pytest
```

Подробный вывод:

```bash
python -m pytest -v
```

Отдельные файлы:

```bash
python -m pytest tests/test_service.py
python -m pytest tests/test_repository.py
python -m pytest tests/test_routes.py
python -m pytest tests/test_notifications.py
```

Один конкретный тест:

```bash
python -m pytest tests/test_service.py::test_update_completed_sends_notification
```

Выбор тестов по имени:

```bash
python -m pytest -k notification
```

Покрытие:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

Весь набор в Docker:

```bash
docker compose run --rm app python -m pytest
```

Отдельный файл и отдельный тест в Docker:

```bash
docker compose run --rm app python -m pytest tests/test_service.py
docker compose run --rm app python -m pytest tests/test_service.py::test_update_completed_sends_notification
```

## Как организованы тесты

| Файл | Что проверяется |
| --- | --- |
| `test_service.py` | Бизнес-логика, валидация, исключения и Mock |
| `test_repository.py` | Чтение и изменение JSON |
| `test_routes.py` | HTTP-контракт Flask API |
| `test_notifications.py` | Внешний HTTP, monkeypatch и сетевые ошибки |

## Изоляция и сброс данных

- Pytest-тесты используют временные копии JSON через `tmp_path` и не изменяют
  `data/tasks.json`.
- Ручные `POST`, `PATCH` и `DELETE` при локальном запуске изменяют настоящий
  `data/tasks.json`.
- В клонированном Git-репозитории исходный файл можно восстановить из папки
  `task-service`:

```bash
git restore data/tasks.json
```

- В Compose нет bind mount для `data/`: изменения происходят внутри контейнера
  и не меняют файл в рабочей директории.
