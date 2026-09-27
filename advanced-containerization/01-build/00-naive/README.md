# 00 — Naive build

Цель: увидеть повторную установку зависимостей после изменения приложения.

Что изменилось: `COPY . .` стоит перед `RUN uv sync`. Это рабочий, но неудобный порядок слоёв.

Команды выполняются из `advanced-containerization/01-build/00-naive`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-build-naive .
docker run -d --name ac-build-naive-demo -p 127.0.0.1:8000:8000 ac-build-naive
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-build-naive-demo`, затем:

```bash
curl -i http://localhost:8000/
```

Ожидаемый результат: HTTP 200, {"message":"Hello, Docker!"}.

## Переключение готового кода

```bash
cp demo_versions/main_v1.py app/main.py
docker build --progress=plain -t ac-build-naive .
cp demo_versions/main_v2.py app/main.py
docker build --progress=plain -t ac-build-naive .
cp demo_versions/main_v1.py app/main.py
```

Смотрите статус именно шага `RUN uv sync`, а не время всей сборки.
`demo_versions` исключён из build context через `.dockerignore`.
Последняя команда восстанавливает исходник; собранный image ещё содержит v2.

При первом переходе v1 → v2 слой установки выполняется заново. Это ожидаемое
учебное поведение. Если v2 уже собирали, он тоже может оказаться cached. Для
повторения исходного опыта нужен свежий builder без этих результатов. `--no-cache`
принудительно повторяет шаги, но сам по себе не доказывает инвалидирование слоёв
из-за изменения кода и не удаляет прежний кеш v2.

## Остановка и очистка

```bash
docker rm -f ac-build-naive-demo
```
