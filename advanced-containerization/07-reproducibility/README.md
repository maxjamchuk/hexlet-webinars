# Тег, digest и lock-файл — резервный блок

Цель: различить имя образа и неизменяемую ссылку на содержимое.
Что изменилось: Dockerfile.digest фиксирует multi-arch OCI index той же линии
`python:3.12-slim`; зависимости обоих вариантов фиксирует `uv.lock`.
Команды из `advanced-containerization/07-reproducibility`.

## Сборка

```bash
docker buildx imagetools inspect python:3.12-slim
docker build -f Dockerfile.tag -t ac-repro-tag .
docker build -f Dockerfile.digest -t ac-repro-digest .
```

Digest получен из registry 2026-09-27:
`sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f`.
Он включает, в частности, linux/amd64 и linux/arm64. Позднее tag может указывать
на другой index; это ожидаемо. В обоих вариантах `uv sync --frozen --no-dev`.

## Запуск и проверка

```bash
docker run -d --name ac-repro-tag-demo -p 127.0.0.1:8000:8000 ac-repro-tag
docker run -d --name ac-repro-digest-demo -p 127.0.0.1:8080:8000 ac-repro-digest
curl -i http://localhost:8000/
curl -i http://localhost:8080/
```

После готовности Uvicorn оба отвечают HTTP 200.
Тег фиксирует имя, digest — конкретное содержимое base image. Одного digest
недостаточно для bit-for-bit воспроизводимости всего результата: влияют зависимости,
build context, repositories, configuration и инструменты сборки. Здесь uv закреплён
тегом 0.8.13, а не digest; это также отдельный вход сборки.

## Очистка

```bash
docker rm -f ac-repro-tag-demo ac-repro-digest-demo
```
