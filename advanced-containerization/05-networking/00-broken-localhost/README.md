# 00-broken-localhost

Цель: проверить адрес API из сети client.
Что изменилось: `API_URL=http://localhost:9000/message`.
localhost внутри client указывает на client; API работает в другом контейнере.
Команды из `advanced-containerization/05-networking/00-broken-localhost`.

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

Ожидается: оба контейнера running; прямой API — HTTP 200; `/proxy` — HTTP 502.
Это ожидаемое учебное поведение. Ответ client: error=upstream unavailable. Внутренний запрос к api:8000 успешен, что локализует проблему в API_URL.

## Остановка и очистка

```bash
docker compose down -v --remove-orphans
```
