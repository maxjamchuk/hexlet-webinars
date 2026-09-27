# 01-service-dns

Цель: проверить адрес API из сети client.
Что изменилось: `API_URL=http://api:8000/message`.
В исправленном stage api имеет healthcheck, client ждёт service_healthy.
Команды из `advanced-containerization/05-networking/01-service-dns`.

## Сборка и запуск

```bash
docker compose build
docker compose up -d --wait --wait-timeout 40
```

## Проверка и диагностика

```bash
curl -i http://localhost:9000/message
curl -i http://localhost:8080/proxy
docker compose ps
docker compose logs client
docker compose logs api
docker compose exec client python -c "import socket; print(socket.gethostbyname('api'))"
docker compose exec client python -c "import urllib.request; print(urllib.request.urlopen('http://api:8000/message').read().decode())"
docker inspect $(docker compose ps -q client)
```

Ожидается: оба контейнера running; прямой API — HTTP 200; `/proxy` — HTTP 200.
Ответ client: upstream.message=Hello from api. Имя api и внутренний порт 8000 работают без публикации порта для межсервисного трафика.

## Остановка и очистка

```bash
docker compose down -v --remove-orphans
```
