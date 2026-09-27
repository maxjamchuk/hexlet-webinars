# PID 1, остановка и здоровье

| Stage | Что увидеть |
|---|---|
| [00-shell-form](00-shell-form/) | Реальное дерево процессов и поведение shell при stop |
| [01-exec-graceful](01-exec-graceful/) | Uvicorn получает SIGTERM, lifespan завершает cleanup |
| [02-healthcheck](02-healthcheck/) | running ≠ healthy; HTTP 503 меняет health status |

Везде используются `APP startup` и `APP shutdown: cleanup complete` с `flush=True`.
Команды самостоятельного запуска и очистки находятся в README стадий.
Shell form не всегда ломает передачу сигналов: результат зависит от shell и его
оптимизаций. Наблюдение нужно связывать с реальным PID 1, а не обобщать на Docker.
