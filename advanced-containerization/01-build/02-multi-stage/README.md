# 02 — Multi-stage build

Цель: отделить инструменты установки от runtime.

Что изменилось: builder содержит uv и готовит `.venv`; runtime получает только Python, `.venv` и `app`.

Команды выполняются из `advanced-containerization/01-build/02-multi-stage`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-build-multi .
docker run -d --name ac-build-multi-demo -p 127.0.0.1:8000:8000 ac-build-multi
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-build-multi-demo`, затем:

```bash
curl -i http://localhost:8000/
```

Ожидаемый результат: HTTP 200, {"message":"Hello, Docker!"}.

## Содержимое runtime

```bash
docker run --rm ac-build-multi python -c "import fastapi; print(fastapi.__version__)"
docker run --rm ac-build-multi sh -c "command -v uv"
docker image ls
```

Импорт успешен. `command -v uv` ничего не печатает и возвращает ненулевой код: это
ожидаемое отсутствие build-инструмента. Builder и runtime используют одинаковую
базу и путь `/app/.venv`: ссылки на Python и shebang остаются рабочими.
`uv sync` не устанавливает сам проект: у него нет build-system.
Сравнивайте реальные размеры images без обещания фиксированного выигрыша.

## Остановка и очистка

```bash
docker rm -f ac-build-multi-demo
```
