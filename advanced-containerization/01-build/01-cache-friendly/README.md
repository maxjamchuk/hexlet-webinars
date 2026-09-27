# 01 — Cache-friendly build

Цель: сохранить слой зависимостей при изменении только кода.

Что изменилось: сначала копируются `pyproject.toml` и `uv.lock`, устанавливаются зависимости, затем копируется `app`.

Команды выполняются из `advanced-containerization/01-build/01-cache-friendly`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-build-cache .
docker run -d --name ac-build-cache-demo -p 127.0.0.1:8000:8000 ac-build-cache
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-build-cache-demo`, затем:

```bash
curl -i http://localhost:8000/
```

Ожидаемый результат: HTTP 200, {"message":"Hello, Docker!"}.

## Переключение готового кода

```bash
cp demo_versions/main_v1.py app/main.py
docker build --progress=plain -t ac-build-cache .
cp demo_versions/main_v2.py app/main.py
docker build --progress=plain -t ac-build-cache .
cp demo_versions/main_v1.py app/main.py
```

Смотрите статус именно шага `RUN uv sync`, а не время всей сборки.
`demo_versions` исключён из build context через `.dockerignore`.
Последняя команда восстанавливает исходник; собранный image ещё содержит v2.

После изменения приложения у шага `RUN uv sync` остаётся `CACHED`.

## Остановка и очистка

```bash
docker rm -f ac-build-cache-demo
```
