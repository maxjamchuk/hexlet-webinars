# Клиентские примеры Movie API

Эти примеры показывают HTTP со стороны клиента: метод, URL, path- и
query-параметры, заголовки, JSON-тело, код состояния и тело ответа. Один и тот
же сценарий приведён для curl и Python requests.

## 1. Запустите API

Из каталога `python_rest/`:

```bash
docker compose up -d --build
```

По умолчанию API доступен по адресу <http://localhost:8080>. Docker Compose
направляет этот внешний порт на внутренний порт контейнера `8000`. Если внешний
порт `8080` занят, выберите другой порт:

```bash
API_PORT=9090 docker compose up -d --build
```

## 2. Настройте адрес клиента

Bash:

```bash
export API_BASE_URL="http://localhost:8080"
```

PowerShell:

```powershell
$env:API_BASE_URL = "http://localhost:8080"
```
Завершающий `/` необязателен: Python-примеры удаляют его автоматически.

## 3. Настройте TMDB-токен

Только пример `04_tmdb_get` обращается к внешнему API. Токен не хранится в
репозитории и передаётся через окружение.

Bash:

```bash
export TMDB_API_TOKEN="your-read-access-token"
```

PowerShell:

```powershell
$env:TMDB_API_TOKEN = "your-read-access-token"
```

## Порядок прохождения

1. `01_get_collection` — коллекция и пагинационный envelope.
2. `02_get_movie` — path-параметр и 404.
3. `03_query_parameters` — фильтры, пагинация и 422.
4. `04_tmdb_get` — внешний read-only API и Bearer-токен.
5. `05_post_movie` — создание ресурса и получение фактического `id`.
6. `06_put_movie` — полная замена по этому `id`.
7. `07_patch_movie` — частичное изменение того же фильма.
8. `08_delete_movie` — удаление выполняется последним.
9. `09_other_methods` — HEAD, OPTIONS и неподдерживаемый TRACE.

После POST скопируйте `id` из JSON или число из заголовка `Location`. Не
предполагайте, что это всегда `1001`:

```bash
python examples/python/06_put_movie.py ACTUAL_ID
python examples/python/07_patch_movie.py ACTUAL_ID
python examples/python/08_delete_movie.py ACTUAL_ID
```

Автоматическая проверка всей последовательности:

```bash
python examples/python/crud_sequence.py
```

Smoke-скрипт удаляет только созданный им временный фильм.

## curl и requests

Подробности запуска curl находятся в [curl/README.md](curl/README.md).
Python-файлы запускаются из корня проекта:

```bash
python examples/python/01_get_collection.py
```

При использовании зависимостей через uv:

```bash
uv run --with-requirements requirements.txt \
  python examples/python/01_get_collection.py
```

| Шаг | curl | Python requests |
|---|---|---|
| Коллекция | `curl/01_get_collection.sh` | `python/01_get_collection.py` |
| Один фильм | `curl/02_get_movie.sh` | `python/02_get_movie.py` |
| Query-параметры | `curl/03_query_parameters.sh` | `python/03_query_parameters.py` |
| TMDB GET | `curl/04_tmdb_get.sh` | `python/04_tmdb_get.py` |
| POST | `curl/05_post_movie.sh` | `python/05_post_movie.py` |
| PUT | `curl/06_put_movie.sh ID` | `python/06_put_movie.py ID` |
| PATCH | `curl/07_patch_movie.sh ID` | `python/07_patch_movie.py ID` |
| DELETE | `curl/08_delete_movie.sh ID` | `python/08_delete_movie.py ID` |
| HEAD/OPTIONS/TRACE | `curl/09_other_methods.sh` | `python/09_other_methods.py` |

## Основные коды ответа

| Код | Значение в примерах |
|---:|---|
| 200 | успешные GET, PUT, PATCH и HEAD |
| 201 | фильм создан; смотрите `Location` |
| 204 | DELETE или OPTIONS без тела |
| 404 | фильм с таким локальным ID не найден |
| 405 | HTTP-метод существует, но API его не поддерживает |
| 422 | path/query/JSON не прошли валидацию |

POST, PUT, PATCH и DELETE изменяют SQLite. Для полного удаления пользовательских
данных и повторной загрузки seed:

```bash
docker compose down -v
docker compose up -d --build
```

`down -v` безвозвратно удаляет пользовательские изменения.
