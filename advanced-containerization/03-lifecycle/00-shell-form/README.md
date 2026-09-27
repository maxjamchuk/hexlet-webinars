# 00 — Shell form и PID 1

Цель: увидеть, кто получает сигнал Docker stop.

Что изменилось: CMD записан строкой, запускаемой через `/bin/sh -c`.

Команды выполняются из `advanced-containerization/03-lifecycle/00-shell-form`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-shell .
docker run -d --name ac-shell-demo -p 127.0.0.1:8000:8000 ac-shell
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-shell-demo`, затем:

```bash
docker top ac-shell-demo
docker stop -t 2 ac-shell-demo
docker logs ac-shell-demo
docker inspect ac-shell-demo
```

Ожидаемый результат: в дереве процессов виден фактический PID 1; логи и ExitCode показывают способ завершения.

Обычный shell может заменить себя приложением или остаться промежуточным
процессом. Если shutdown hook отсутствует и завершение произошло после timeout,
сопоставьте это с `docker top`. Это ожидаемое учебное поведение для shell, который
не передаёт сигнал дочернему процессу. Тезис «shell form всегда ломает SIGTERM» неверен.

## Остановка и очистка

```bash
docker rm -f ac-shell-demo
```
