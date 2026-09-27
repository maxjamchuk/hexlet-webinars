# Пользователь процесса и права файлов

Один небольшой API, три независимых образа. `GET /identity` читает реальный UID,
`POST /write` пишет `/app/data/message.txt`.

| Stage | Пользователь | Результат записи |
|---|---|---|
| [00-root](00-root/) | root / 0 | 200 |
| [01-non-root-broken](01-non-root-broken/) | app / 10001 | 500 permission denied |
| [02-non-root-fixed](02-non-root-fixed/) | app / 10001 | 200 |

Исправляется владелец только `/app/data`. Код и окружение остаются недоступными
для записи пользователю приложения. Команды запуска и cleanup — в README стадий.
