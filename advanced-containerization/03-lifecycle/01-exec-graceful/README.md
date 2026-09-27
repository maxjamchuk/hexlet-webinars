# 01 — Exec form и graceful shutdown

Цель: дать приложению получить SIGTERM и завершить cleanup.

Что изменилось: CMD — JSON-массив; Uvicorn является PID 1.

Команды выполняются из `advanced-containerization/03-lifecycle/01-exec-graceful`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-lifecycle .
docker run -d --name ac-lifecycle-demo -p 127.0.0.1:8000:8000 ac-lifecycle
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-lifecycle-demo`, затем:

```bash
curl -i http://localhost:8000/
docker top ac-lifecycle-demo
docker stop ac-lifecycle-demo
docker logs ac-lifecycle-demo
docker inspect ac-lifecycle-demo
```

Ожидаемый результат: HTTP 200, затем APP shutdown: cleanup complete и ExitCode 0.


## Остановка и очистка

```bash
docker rm -f ac-lifecycle-demo
```
