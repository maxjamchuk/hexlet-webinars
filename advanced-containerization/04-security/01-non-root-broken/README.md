# Non-root: неверные права

Цель: проверить влияние UID и владельца каталога на запись.

Что изменилось: добавлен USER app (10001), но каталог data оставлен root:root с 755.

Команды выполняются из `advanced-containerization/04-security/01-non-root-broken`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-nonroot-broken .
docker run -d --name ac-nonroot-broken-demo -p 127.0.0.1:8000:8000 ac-nonroot-broken
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-nonroot-broken-demo`, затем:

```bash
curl -i http://localhost:8000/identity
curl -i -X POST http://localhost:8000/write
```

Ожидаемый результат: uid=10001, user=app, запись HTTP 500 с error=permission denied.

Это ожидаемое учебное поведение. PermissionError обрабатывается: клиент получает короткий JSON без traceback.

## Остановка и очистка

```bash
docker rm -f ac-nonroot-broken-demo
```
