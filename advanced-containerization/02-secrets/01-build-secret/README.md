# 01 — BuildKit secret mount

Цель: использовать секрет во время сборки без сохранения его в image.
Что изменилось: `required=true` требует секрет; RUN читает его, проверяет непустое
значение и пишет только нейтральный `build-result.txt`.
Команды из `advanced-containerization/02-secrets/01-build-secret`.

## Сборка, запуск и проверка

```bash
cp demo-secret.example .demo-secret
docker build --secret id=demo_token,src=.demo-secret -t ac-secret-good .
docker run --rm ac-secret-good cat /app/build-result.txt
docker image inspect ac-secret-good
docker run --rm ac-secret-good env
docker run --rm ac-secret-good sh -c "test ! -e /run/secrets/demo_token"
```

Ожидается `private resource fetched`. В metadata/env нет токена, путь secret mount
в runtime отсутствует. Пример намеренно не выводит и не копирует токен из mount.

## Ожидаемая ошибка

```bash
docker build --no-cache -t ac-secret-good .
```

Сборка завершается ненулевым кодом: `secret demo_token: not found`.
Это ожидаемое учебное поведение. `--no-cache` нужен, чтобы проверка не была пропущена
из-за ранее успешно закешированного RUN.

## Очистка

Контейнеры удаляются через `--rm`.

```bash
rm .demo-secret
docker image rm ac-secret-good
```
