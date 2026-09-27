# Compose networking

Два сервиса в каждом независимом stage: `api` и `client`. Без БД и внешних API.
[00-broken-localhost](00-broken-localhost/) обращается к самому client через
`localhost:9000`. [01-service-dns](01-service-dns/) использует `api:8000`.

`9000` — опубликованный порт host; `8000` — порт API внутри сети Compose.
Сервисное имя `api` разрешается внутренним DNS. В исправленном stage
`depends_on: condition: service_healthy` ждёт готовности api при старте.
Это не постоянный мониторинг доступности и не автоматическое восстановление связи.
См. [порядок старта Compose](https://docs.docker.com/compose/how-tos/startup-order/).

В README обеих стадий есть полный маршрут `ps → logs → exec → inspect`.
Если host ports заняты, задайте `CLIENT_PORT` и `API_PORT` в своём shell.
Например PowerShell: `$env:CLIENT_PORT="18080"; $env:API_PORT="19000"`.
В Bash: `export CLIENT_PORT=18080 API_PORT=19000`. Затем используйте эти порты в curl.
Smoke-check передаёт значения `0`: Docker сам выбирает свободные порты, скрипт
узнаёт их через `docker compose port`.
