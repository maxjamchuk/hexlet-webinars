# Память и OOM — резервный блок

Цель: увидеть рост памяти и принудительное завершение по лимиту.
Что изменилось: вместо FastAPI — короткий stdlib-скрипт. Каждую секунду он сохраняет
ещё 4 MiB реально заполненных байтов и печатает объём с `flush=True`.
Команды из `advanced-containerization/06-resources`.

## Сборка и запуск

```bash
docker build -t ac-memory .
docker run --name ac-memory-demo --memory=64m --memory-swap=64m ac-memory
```

В отдельном терминале:

```bash
docker stats ac-memory-demo
```

## Проверка

После завершения процесса:

```bash
docker logs ac-memory-demo
docker inspect ac-memory-demo
```

Ожидаемое учебное поведение: растёт `allocated`, затем container завершён;
на Linux/Docker Desktop `State.OOMKilled=true`, `State.ExitCode=137`.
Сопоставляйте оба поля: один код 137 не доказывает OOM.
Лимит 64 MiB включает интерпретатор и прочие расходы, не только сохранённые блоки.
Ориентир — 10–40 секунд, время зависит от среды. Процесс не ловит и не маскирует OOM.
Не запускайте скрипт напрямую без ограничения памяти.

## Очистка

```bash
docker rm -f ac-memory-demo
```
