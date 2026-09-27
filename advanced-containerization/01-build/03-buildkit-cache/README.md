# 03 — BuildKit package cache

Цель: различить Docker layer cache и кеш скачанных пакетов.

Что изменилось: mount `/root/.cache/uv` сохраняет package cache между выполнениями RUN; `UV_LINK_MODE=copy` копирует файлы из mount в окружение.

Команды выполняются из `advanced-containerization/01-build/03-buildkit-cache`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-build-buildkit .
docker run -d --name ac-build-buildkit-demo -p 127.0.0.1:8000:8000 ac-build-buildkit
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-build-buildkit-demo`, затем:

```bash
curl -i http://localhost:8000/
```

Ожидаемый результат: HTTP 200, {"message":"Hello, Docker!"}.

## Принудительно повторить RUN

```bash
docker build --progress=plain --build-arg CACHE_BUST=1 -t ac-build-buildkit .
docker build --progress=plain --build-arg CACHE_BUST=2 -t ac-build-buildkit .
```

`CACHE_BUST` участвует в `echo` внутри RUN. Во второй сборке этот слой выполняется
снова, но uv использует содержимое cache mount. Смотрите `Installed` и отсутствие
повторных `Downloading` для уже полученных пакетов. Не сравнивайте только секунды.
Для повторного показа можно использовать новые значения `CACHE_BUST`.

## Остановка и очистка

```bash
docker rm -f ac-build-buildkit-demo
```
