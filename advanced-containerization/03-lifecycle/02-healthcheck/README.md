# 02 — Running не значит healthy

Цель: сломать health без остановки процесса.

Что изменилось: `/health` проверяет маркер `/tmp/unhealthy`; HEALTHCHECK использует urllib стандартной библиотеки.

Команды выполняются из `advanced-containerization/03-lifecycle/02-healthcheck`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-health .
docker run -d --name ac-health-demo -p 127.0.0.1:8000:8000 ac-health
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-health-demo`, затем:

```bash
curl -i http://localhost:8000/health
docker inspect ac-health-demo
```

Ожидаемый результат: HTTP 200 и State.Health.Status=healthy после первых проверок.

## Поломка и восстановление

```bash
docker exec ac-health-demo touch /tmp/unhealthy
curl -i http://localhost:8000/health
docker inspect ac-health-demo
```

HTTP 503 сразу; через несколько проверок `unhealthy`, но `State.Status=running`.
Это ожидаемое учебное поведение. Повторяйте inspect до смены статуса.

```bash
docker exec ac-health-demo rm /tmp/unhealthy
docker inspect ac-health-demo
curl -i http://localhost:8000/health
```

После следующей успешной проверки — `healthy`, HTTP 200. Интервал 2s, timeout 1s,
retries 2. Healthcheck сам по себе не перезапускает контейнер.

## Остановка и очистка

```bash
docker rm -f ac-health-demo
```
