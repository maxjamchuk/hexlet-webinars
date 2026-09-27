# 00 — Токен в ENV

Цель: доказать сохранение секрета в metadata и runtime.
Что изменилось: значение ARG записывается в ENV. Это ожидаемое учебное поведение.
Команды из `advanced-containerization/02-secrets/00-bad`.

## Сборка, запуск и проверка

```bash
docker build --build-arg DEMO_TOKEN=demo-token-for-build -t ac-secret-bad .
docker image inspect ac-secret-bad
docker run --rm ac-secret-bad env
```

Ожидается `DEMO_TOKEN=demo-token-for-build` в Config.Env и выводе env.
В production такой способ передачи секретов не подходит.

## Очистка

Контейнер уже удалён благодаря `--rm`. Учебный image можно удалить:

```bash
docker image rm ac-secret-bad
```
