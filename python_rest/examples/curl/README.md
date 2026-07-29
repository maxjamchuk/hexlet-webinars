# curl-примеры

Файлы рассчитаны на Bash и запускаются из каталога `python_rest/`:

```bash
export API_BASE_URL="http://localhost:8080"
bash examples/curl/01_get_collection.sh
```

TMDB API Key v3 задаётся только через окружение и передаётся в
query-параметре `api_key`:

```bash
export TMDB_API_KEY="your-api-key-v3"
bash examples/curl/04_tmdb_get.sh
```

В PowerShell переменные задаются так:

```powershell
$env:API_BASE_URL = "http://localhost:8080"
$env:TMDB_API_KEY = "your-api-key-v3"
```

В Windows PowerShell используйте `curl.exe`, если имя `curl` связано с другим
командлетом. Эквивалентные однострочные команды:

```powershell
curl.exe -i "$env:API_BASE_URL/movies?limit=3"
curl.exe -i -X POST "$env:API_BASE_URL/movies" -H "Content-Type: application/json" --data '{"title":"Workshop Movie"}'
curl.exe -i -G "https://api.themoviedb.org/3/search/movie" --data-urlencode "api_key=$env:TMDB_API_KEY" --data-urlencode "query=Interstellar" --data-urlencode "language=en-US" --data-urlencode "page=1"
```

Bash-эквиваленты:

```bash
curl -i "$API_BASE_URL/movies?limit=3"
curl -i -X POST "$API_BASE_URL/movies" -H "Content-Type: application/json" --data '{"title":"Workshop Movie"}'
curl -i -G "https://api.themoviedb.org/3/search/movie" --data-urlencode "api_key=$TMDB_API_KEY" --data-urlencode "query=Interstellar" --data-urlencode "language=en-US" --data-urlencode "page=1"
```

JSON можно необязательно передать в `python -m json.tool`, но сами примеры не
требуют jq, httpie, Postman или других утилит.

Изменяющие шаги выполняются последовательно: POST возвращает фактический ID,
этот ID передаётся в PUT и PATCH, а DELETE запускается последним:

```bash
bash examples/curl/06_put_movie.sh ACTUAL_ID
bash examples/curl/07_patch_movie.sh ACTUAL_ID
bash examples/curl/08_delete_movie.sh ACTUAL_ID
```

TRACE — существующий HTTP-метод, но Movie API его не поддерживает. Отдельного
обработчика TRACE нет, поэтому ожидается `405 Method Not Allowed`.
