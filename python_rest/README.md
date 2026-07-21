# Python: REST API

Материалы к вебинару по работе с REST API из Python.

Вебинар построен вокруг готового учебного Movie API. На нём удобно разобрать устройство HTTP-запроса и ответа, методы GET, POST, PUT, PATCH и DELETE, path- и query-параметры, заголовки, JSON, коды состояния, Bearer-токены и работу с API через `curl` и библиотеку `requests`.

FastAPI используется как готовая серверная песочница. Основная тема вебинара — клиентская работа с HTTP API, а не устройство FastAPI-приложения.

## Презентация

[Открыть презентацию в Google Slides](https://docs.google.com/presentation/d/1m9xFHPvJvHq5JG8hT64MC5wjygzI1BIik-Ttt2HWr9Q/edit)

## Что понадобится на вебинаре

Для основной части нужны:

- Docker с поддержкой Docker Compose;
- терминал;
- Python для примеров с `requests`;
- TMDB API Read Access Token для демонстрации внешнего API.

Учебный API запускается одной командой и не требует отдельно установленной базы данных.

| Материал | Для чего нужен |
|----------|----------------|
| `compose.yaml` | Запуск Movie API через Docker Compose. |
| `examples/curl/` | Последовательные HTTP-запросы через `curl`. |
| `examples/python/` | Те же сценарии через Python и `requests`. |
| `data/movies.json` | Исходный набор из 1000 фильмов. |
| `examples/README.md` | Подробное описание порядка прохождения примеров. |

## Структура проекта

| Путь | Описание |
|------|----------|
| `app/` | Реализация Movie API на FastAPI с SQLite. |
| `data/movies.json` | Seed-файл с 1000 фильмами. |
| `examples/curl/` | Примеры запросов через `curl`. |
| `examples/python/` | Примеры запросов через `requests`. |
| `examples/python/crud_sequence.py` | Автоматический проход полного CRUD-сценария. |
| `scripts/export_movies_from_mongo.py` | Скрипт подготовки seed-файла из MongoDB Kadracoon. |
| `tests/` | Тесты API, seed-инициализации, экспортёра и TMDB-примера. |
| `Dockerfile` | Сборка контейнера с FastAPI-приложением. |
| `compose.yaml` | Запуск контейнера и persistent volume для SQLite. |
| `.env.example` | Пример пользовательских переменных окружения. |
| `requirements.txt` | Зависимости приложения, тестов и Python-примеров. |
| `README.md` | Общее описание материалов вебинара. |

## Запуск Movie API

Перейдите в каталог вебинара:

```bash
cd python_rest
```

Запустите приложение:

```bash
docker compose up --build
```

После запуска доступны:

- Movie API: [http://localhost:8080/movies](http://localhost:8080/movies)
- Swagger UI: [http://localhost:8080/docs](http://localhost:8080/docs)

Docker публикует внешний порт `8080`, а внутри контейнера приложение продолжает работать на порту `8000`:

```text
localhost:8080 → container:8000
```

Остановить приложение:

```bash
docker compose down
```

При обычной остановке созданные и изменённые фильмы сохраняются в Docker volume.

## Полный сброс данных

Чтобы удалить рабочую SQLite-базу и снова загрузить исходные 1000 фильмов:

```bash
docker compose down -v
docker compose up --build
```

Команда `docker compose down -v` удаляет все изменения, сделанные через POST, PUT, PATCH и DELETE.

## Переменные окружения

Значения по умолчанию:

```dotenv
API_PORT=8080
API_BASE_URL=http://localhost:8080
TMDB_API_TOKEN=
```

Копировать `.env.example` необязательно: Docker Compose и клиентские примеры уже используют порт `8080` по умолчанию.

При необходимости можно создать локальный `.env`:

```bash
cp .env.example .env
```

Настоящий TMDB-токен нельзя добавлять в Git.

## Запуск curl-примеров

Примеры рассчитаны на Bash и запускаются из каталога `python_rest/`.

Первый запрос:

```bash
bash examples/curl/01_get_collection.sh
```

Все curl-примеры описаны в отдельном файле:

[`examples/curl/README.md`](examples/curl/README.md)

В Windows PowerShell может понадобиться команда `curl.exe`, потому что имя `curl` иногда связано с другим командлетом.

## Запуск Python-примеров

Установить зависимости можно обычным способом:

```bash
python -m pip install -r requirements.txt
```

После этого:

```bash
python examples/python/01_get_collection.py
```

Либо запустить пример через `uv` без отдельной установки зависимостей в текущее окружение:

```bash
uv run --with-requirements requirements.txt \
  python examples/python/01_get_collection.py
```

На некоторых системах команда Python называется `python3`.

## Рекомендуемый порядок прохождения

### 1. Получение коллекции

```bash
bash examples/curl/01_get_collection.sh
python examples/python/01_get_collection.py
```

Запрос:

```http
GET /movies?limit=3
```

На этом примере разбираются:

- метод GET;
- URL;
- query-параметр `limit`;
- статус `200 OK`;
- JSON-ответ;
- поля пагинации `total`, `limit` и `offset`.

### 2. Получение одного ресурса

```bash
bash examples/curl/02_get_movie.sh
python examples/python/02_get_movie.py
```

Запрос существующего фильма:

```http
GET /movies/1
```

Запрос отсутствующего фильма:

```http
GET /movies/999999
```

Здесь видно различие между:

- `200 OK` — ресурс найден;
- `404 Not Found` — запрос корректен, но такого ресурса нет.

### 3. Query-параметры и валидация

```bash
bash examples/curl/03_query_parameters.sh
python examples/python/03_query_parameters.py
```

Примеры:

```text
/movies?title=whiplash
/movies?year=2013
/movies?limit=5&offset=10
/movies?title=whiplash&year=2013
```

Ошибочный параметр:

```text
/movies?limit=0
```

Сервер возвращает:

```text
422 Unprocessable Content
```

Главная мысль: `404` означает отсутствие ресурса, а `422` — ошибку во входных данных.

### 4. Внешний TMDB API

Для выполнения примера нужен TMDB API Read Access Token.

Bash:

```bash
export TMDB_API_TOKEN="your-read-access-token"
```

PowerShell:

```powershell
$env:TMDB_API_TOKEN = "your-read-access-token"
```

Запуск:

```bash
bash examples/curl/04_tmdb_get.sh
python examples/python/04_tmdb_get.py
```

Сначала выполняется поиск фильма:

```http
GET /3/search/movie?query=Interstellar&language=en-US&page=1
```

Затем ID из результата используется в следующем запросе:

```http
GET /3/movie/{movie_id}
```

Токен передаётся через заголовок:

```http
Authorization: Bearer <token>
```

### 5. Создание ресурса через POST

```bash
bash examples/curl/05_post_movie.sh
python examples/python/05_post_movie.py
```

Минимальное тело:

```json
{
  "title": "Workshop Movie"
}
```

Успешный ответ:

```text
201 Created
```

Сервер самостоятельно назначает локальный `id` и возвращает заголовок:

```text
Location: /movies/{id}
```

Полученный ID нужно сохранить для следующих шагов. Нельзя предполагать, что он всегда равен `1001`.

### 6. Полная замена через PUT

Подставьте ID, полученный после POST:

```bash
bash examples/curl/06_put_movie.sh ACTUAL_ID
python examples/python/06_put_movie.py ACTUAL_ID
```

PUT требует передать полное представление всех изменяемых полей.

Пропущенное обязательное поле приводит к:

```text
422 Unprocessable Content
```

### 7. Частичное изменение через PATCH

```bash
bash examples/curl/07_patch_movie.sh ACTUAL_ID
python examples/python/07_patch_movie.py ACTUAL_ID
```

PATCH передаёт только те поля, которые нужно изменить:

```json
{
  "vote_average": 9.0,
  "genres": ["Drama", "Comedy"]
}
```

Nullable-поле можно очистить явным `null`:

```json
{
  "overview": null
}
```

### 8. Удаление через DELETE

DELETE выполняется последним:

```bash
bash examples/curl/08_delete_movie.sh ACTUAL_ID
python examples/python/08_delete_movie.py ACTUAL_ID
```

Успешное удаление:

```text
204 No Content
```

У ответа нет тела, поэтому после `204` не нужно вызывать:

```python
response.json()
```

Следующий GET и повторный DELETE возвращают:

```text
404 Not Found
```

### 9. HEAD, OPTIONS и TRACE

```bash
bash examples/curl/09_other_methods.sh
python examples/python/09_other_methods.py
```

В учебном API:

| Метод | Результат |
|-------|-----------|
| HEAD | Возвращает заголовки без тела ответа. |
| OPTIONS | Возвращает разрешённые методы в заголовке `Allow`. |
| TRACE | Не поддерживается и возвращает `405 Method Not Allowed`. |

## Полный CRUD-сценарий

Скрипт автоматически создаёт временный фильм, изменяет его и удаляет:

```bash
python examples/python/crud_sequence.py
```

Последовательность:

```text
POST → PUT → PATCH → GET → DELETE → GET / 404
```

Скрипт не заменяет отдельные учебные примеры, но подходит для итоговой демонстрации или быстрой проверки API.

## Какие темы можно отработать

### Устройство HTTP-запроса

```text
method + URL + headers + body
```

Запрос состоит не только из адреса. Метод сообщает намерение клиента, заголовки передают дополнительный контекст, а тело содержит данные.

### Path- и query-параметры

```text
/movies/1
```

`1` — path-параметр, который выбирает конкретный ресурс.

```text
/movies?year=2013&limit=5
```

`year` и `limit` — query-параметры, которые уточняют выборку.

### Коды состояния

На вебинаре используются:

- `200 OK`;
- `201 Created`;
- `204 No Content`;
- `404 Not Found`;
- `405 Method Not Allowed`;
- `422 Unprocessable Content`.

### curl и requests

Один HTTP-запрос можно отправить разными клиентами.

Через curl:

```bash
curl "$API_BASE_URL/movies?limit=3"
```

Через requests:

```python
requests.get(
    f"{base_url}/movies",
    params={"limit": 3},
    timeout=10,
)
```

Протокол и серверный контракт остаются теми же.

### PUT и PATCH

PUT полностью заменяет изменяемое представление ресурса.

PATCH изменяет только переданные поля.

### Работа с секретами

Токены нельзя хранить прямо в исходном коде:

```python
token = os.getenv("TMDB_API_TOKEN")
```

Секрет передаётся через окружение и HTTP-заголовок, но не попадает в репозиторий.

## Запуск тестов

```bash
uv run --with-requirements requirements.txt \
  python -m unittest discover -s tests -v
```

Тесты не выполняют реальные запросы к TMDB: внешние ответы подменяются через mock.

## Главная идея вебинара

REST API — это HTTP-контракт между клиентом и сервером.

Клиенту не обязательно знать, написан сервер на FastAPI, Django, Flask, Go или Java. Для работы с API ему достаточно знать:

- метод;
- URL;
- параметры;
- заголовки;
- формат тела;
- возможные коды ответа.

Один и тот же контракт можно использовать из терминала через `curl`, из Python через `requests` или из другого HTTP-клиента.

Хороший признак:

> клиент формирует запрос по документированному контракту и проверяет код ответа.

Плохой признак:

> клиент предполагает конкретный ID, игнорирует ошибки, не задаёт timeout или хранит токен прямо в коде.

## Статус материалов

Материалы рассчитаны на воркшоп продолжительностью от 90 до 120 минут.

Основной сценарий включает GET, внешний TMDB API и полный жизненный цикл ресурса. HEAD, OPTIONS, TRACE, мини-тесты и автоматический CRUD-сценарий можно использовать как резерв.