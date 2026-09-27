# Non-root: права исправлены

Цель: проверить влияние UID и владельца каталога на запись.

Что изменилось: владелец только /app/data изменён на app:app; USER остаётся app.

Команды выполняются из `advanced-containerization/04-security/02-non-root-fixed`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-nonroot-fixed .
docker run -d --name ac-nonroot-fixed-demo -p 127.0.0.1:8000:8000 ac-nonroot-fixed
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-nonroot-fixed-demo`, затем:

```bash
curl -i http://localhost:8000/identity
curl -i -X POST http://localhost:8000/write
```

Ожидаемый результат: uid=10001, user=app, запись HTTP 200.


## Остановка и очистка

```bash
docker rm -f ac-nonroot-fixed-demo
```
