# Root

Цель: проверить влияние UID и владельца каталога на запись.

Что изменилось: USER не задан, процесс работает как root.

Команды выполняются из `advanced-containerization/04-security/00-root`.

## Сборка и запуск

```bash
docker build --progress=plain -t ac-root .
docker run -d --name ac-root-demo -p 127.0.0.1:8000:8000 ac-root
```

## Проверка

Дождитесь сообщения Uvicorn о готовности в `docker logs ac-root-demo`, затем:

```bash
curl -i http://localhost:8000/identity
curl -i -X POST http://localhost:8000/write
```

Ожидаемый результат: uid=0, user=root, запись HTTP 200.


## Остановка и очистка

```bash
docker rm -f ac-root-demo
```
