# Сборка: от порядка слоёв до package cache

Четыре независимых каталога с одинаковым FastAPI. В каждом есть собственные
`pyproject.toml`, `uv.lock`, Dockerfile и готовые `demo_versions`.

| Stage | Что меняется | Наблюдение |
|---|---|---|
| [00-naive](00-naive/) | COPY всего контекста перед uv sync | Изменение кода повторяет установку |
| [01-cache-friendly](01-cache-friendly/) | Зависимости копируются первыми | RUN uv sync остаётся CACHED |
| [02-multi-stage](02-multi-stage/) | Отдельные builder/runtime | FastAPI работает, uv отсутствует |
| [03-buildkit-cache](03-buildkit-cache/) | Cache mount для uv | Повторный RUN использует кеш пакетов |

Команды сборки, запуска, проверки и очистки — в README каждой стадии.
Первое получение базовых images и пакетов требует сети. Прогрейте образы до занятия.
Размеры можно посмотреть через `docker image ls`; время и размер зависят от среды.
