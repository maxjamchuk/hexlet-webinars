# Продвинутая контейнеризация

Практический воркшоп Hexlet для студентов 8-го модуля. Примеры подходят и для
более ранних модулей, если уже знакомы Docker image/container, Dockerfile,
`build`, `run`, опубликованные порты и базовый Compose.

Цель — научиться наблюдать и исправлять конкретные проблемы сборки и запуска:
**что не так → как увидеть → как исправить → что изменилось**.
После занятия студент умеет проверить кеширование, содержимое image, сигналы,
health status, пользователя процесса, права записи и адресацию между контейнерами.
FastAPI — минимальная нагрузка для Docker, а не предмет занятия.

## Презентация

[Открыть презентацию в Google Slides](https://docs.google.com/presentation/d/1mP537X00TmYawKprcY-J2EN8RIrt7-z0q1vF29-z0h0/edit?usp=sharing)

## Окружение

- Git, Docker с Linux containers и BuildKit, Docker Compose v2.
- На Windows/macOS — запущенный Docker Desktop; на Linux — доступный daemon.
- Python 3.12+ для smoke-check. В images используется `python:3.12-slim`.
- uv 0.8.13 закреплён в Dockerfile; локальный uv нужен только для обновления locks.
- Сеть при первом получении images и зависимостей из Docker Hub, GHCR и PyPI.

```bash
docker version
docker compose version
python --version
uv --version
```

В каждом Python stage есть собственные `pyproject.toml` и `uv.lock`.
Используются `fastapi[standard]>=0.115,<1`, в networking также `httpx>=0.28,<1`.
Docker устанавливает зависимости через `uv sync --frozen --no-dev`.
Secret/resource stages используют только стандартную библиотеку базового image.

Команды README записаны в одну строку и пригодны для Bash и PowerShell.
В Windows PowerShell 5 вместо алиаса `curl` используйте `curl.exe`.
Запускайте команды из указанного каталога stage. Все stages независимы:
файлы соседних проектов не импортируются и ранее запущенные сервисы не нужны.

## Карта и маршрут на 90 минут

| Блок | Время | Stages и наблюдение |
|---|---:|---|
| Введение | 7 мин | Цели воркшопа и исходные знания Docker |
| [01-build](01-build/) | 18 мин | naive → cache-friendly → multi-stage → BuildKit cache; слои, runtime и package cache |
| [02-secrets](02-secrets/) | 10 мин | bad ENV → build secret; где остаётся токен |
| [03-lifecycle](03-lifecycle/) | 17 мин | shell form → exec graceful → healthcheck; PID 1, stop, running ≠ healthy |
| [04-security](04-security/) | 12 мин | root → broken non-root → fixed non-root; UID и владельцы файлов |
| [05-networking](05-networking/) | 18 мин | broken localhost → service DNS; ps, logs, exec и inspect |
| Итог | 8 мин | Основные выводы и вопросы |

Резервные **+30 минут**: [06-resources](06-resources/) — 12 минут на память/OOM,
[07-reproducibility](07-reproducibility/) — 10 минут на tag/digest/lock,
ещё 8 минут — концептуальное обсуждение orchestration/Kubernetes без практики.
Основной маршрут рассчитан на заранее загруженные images и зависимости.

## Быстрый запуск

Из корня репозитория перейдите в выбранный stage из таблицы. Для обычного API
шаблон запуска одинаковый; исключения — secrets, Compose, resources и digest.

```bash
cd advanced-containerization/01-build/00-naive
docker build --progress=plain -t ac-build-naive .
docker run -d --name ac-build-naive-demo -p 127.0.0.1:8000:8000 ac-build-naive
docker logs ac-build-naive-demo
curl -i http://localhost:8000/
docker rm -f ac-build-naive-demo
```

Повторите HTTP-запрос после сообщения Uvicorn о готовности. Точные команды
сборки, запуска, проверки и cleanup есть **в README каждого stage**:

| Stage | Image / способ запуска |
|---|---|
| [01-build/00-naive](01-build/00-naive/) | `ac-build-naive`, обычный API |
| [01-build/01-cache-friendly](01-build/01-cache-friendly/) | `ac-build-cache`, обычный API |
| [01-build/02-multi-stage](01-build/02-multi-stage/) | `ac-build-multi`, обычный API |
| [01-build/03-buildkit-cache](01-build/03-buildkit-cache/) | `ac-build-buildkit`, обычный API; два CACHE_BUST |
| [02-secrets/00-bad](02-secrets/00-bad/) | `docker build --build-arg DEMO_TOKEN=demo-token-for-build -t ac-secret-bad .`, затем `docker run --rm ac-secret-bad env` |
| [02-secrets/01-build-secret](02-secrets/01-build-secret/) | `cp demo-secret.example .demo-secret`, `docker build --secret id=demo_token,src=.demo-secret -t ac-secret-good .`, `docker run --rm ac-secret-good` |
| [03-lifecycle/00-shell-form](03-lifecycle/00-shell-form/) | `ac-shell`, обычный API |
| [03-lifecycle/01-exec-graceful](03-lifecycle/01-exec-graceful/) | `ac-lifecycle`, обычный API |
| [03-lifecycle/02-healthcheck](03-lifecycle/02-healthcheck/) | `ac-health`, обычный API и `/health` |
| [04-security/00-root](04-security/00-root/) | `ac-root`, API `/identity` и `POST /write` |
| [04-security/01-non-root-broken](04-security/01-non-root-broken/) | `ac-nonroot-broken`, тот же API |
| [04-security/02-non-root-fixed](04-security/02-non-root-fixed/) | `ac-nonroot-fixed`, тот же API |
| [05-networking/00-broken-localhost](05-networking/00-broken-localhost/) | `docker compose build`, `docker compose up -d --wait --wait-timeout 40` |
| [05-networking/01-service-dns](05-networking/01-service-dns/) | Те же команды Compose; host `/proxy` на 8080, `/message` на 9000 |
| [06-resources](06-resources/) | `docker build -t ac-memory .`, `docker run --name ac-memory-demo --memory=64m --memory-swap=64m ac-memory` |
| [07-reproducibility](07-reproducibility/) | `docker build -f Dockerfile.tag -t ac-repro-tag .` и `docker build -f Dockerfile.digest -t ac-repro-digest .`; оба — обычные API |

Останавливайте предыдущий API перед занятием того же host port. Для сравнения
кеша готовые `main_v1.py`/`main_v2.py` копируются из `demo_versions`, писать код
вручную не нужно. После демонстрации восстановите `app/main.py` из `main_v1.py`.

## Намеренные ошибки

| Сценарий | Ожидаемый результат |
|---|---|
| Bad secret | Учебный токен виден в metadata и runtime ENV |
| Build secret без `--secret`, с `--no-cache` | Сборка падает: required secret отсутствует |
| Broken non-root | UID 10001, запись возвращает 500 permission denied |
| Broken localhost | API доступен с host, client возвращает контролируемый 502 |
| Маркер `/tmp/unhealthy` | `/health` возвращает 503; контейнер running + unhealthy |
| Memory limit | Процесс завершён; ожидаются OOMKilled=true и ExitCode=137 |

Это учебные наблюдения, а не дефекты проекта. Shell-form shutdown наблюдается
на конкретной среде: наличие shell не гарантирует поломку передачи сигналов.

## Smoke-check

Из `advanced-containerization`:

```bash
python tools/smoke_check.py
python tools/smoke_check.py --include-bonus
```

Скрипт использует только Python stdlib, собирает images, запускает настоящие
контейнеры, делает HTTP-запросы, проверяет metadata, UID, shutdown и health.
Для networking используется настоящий Compose с диагностикой DNS/HTTP из client.
Режим bonus добавляет OOM и обе сборки reproducibility. `[SKIP]` допускается
только когда daemon явно сообщает отсутствие поддержки memory/swap limits.

Скрипт проверяет Docker/daemon/Compose, ограничивает ожидания, назначает уникальные
имена `hexlet-ac-smoke-*` и динамические порты. В `finally` удаляет свои контейнеры,
а Compose останавливает и удаляет локальные images текущего уникального проекта
через `down -v --remove-orphans --rmi local`. Пользовательские
контейнеры не затрагиваются; очистки общего build cache нет.
Подробные команды, stdout/stderr и времена сохраняются в игнорируемом `.smoke-logs/`.

Успех: строки `[OK]`, затем `All required demos behave as expected.`, exit code 0.
Неожиданная ошибка: `[FAIL]`, диагностика и ненулевой код.

## Troubleshooting

- Daemon недоступен: запустите Docker Desktop/службу, проверьте `docker version`.
- Ошибка TLS/registry timeout: проверьте сеть и повторите `docker pull python:3.12-slim`
  и `docker pull ghcr.io/astral-sh/uv:0.8.13`. Не отключайте проверку TLS.
- Порт занят: остановите свой предыдущий demo или измените host port. Для Compose
  доступны `CLIENT_PORT`/`API_PORT`; smoke-check выбирает свободные порты автоматически.
- Имя контейнера занято: удалите только свой контейнер из команды соответствующего
  stage. Smoke-check использует новые имена при каждом запуске.
- Health ещё `starting`: повторите inspect через несколько секунд. `running`
  не означает, что HTTP уже готов; Compose fixed stage ждёт `service_healthy`.
- Secret build неожиданно прошёл без secret: повторите с `--no-cache`.
- Кеш уже прогрет предыдущим занятием: изменение на ранее собранный v2 также
  может попасть в cache. Для исходного опыта используйте свежий builder;
  `--no-cache` не удаляет прежние результаты и не доказывает саму причину инвалидирования.
- Нет memory/swap limit: ресурсный demo требует поддерживающий их Linux runtime.

Времена не являются assertions: холодная сборка может занимать 20–120 секунд и
больше при медленной сети; тёплая — несколько секунд; health — около 2–6 секунд;
Compose после сборки — около 2–10 секунд; OOM — около 10–40 секунд.

## Фактическая проверка

Проверено 2026-09-27 на Docker Desktop, Linux containers, linux/amd64:
Docker client/server 28.5.1, Compose v2.40.3-desktop.1, host Python 3.13.2,
host uv 0.9.11. В images: Python 3.12.14 и uv 0.8.13; locks созданы и проверены
uv 0.8.13. Обычный и bonus smoke-check завершились кодом 0 без `[SKIP]`.

| Проверка | Наблюдение |
|---|---|
| Naive, v1 → v2 | RUN uv sync выполняется заново; rebuild 6,4 с |
| Cache-friendly, v1 → v2 | RUN uv sync CACHED; rebuild 1,7 с |
| BuildKit CACHE_BUST 1 → 2 | RUN повторился, Installed 44 packages; повторных Downloading нет |
| Shell / exec | Shell: отдельный `/bin/sh`, нет shutdown hook, exit 137; exec: hook есть, exit 0 |
| Health | healthy → unhealthy за 4,2 с, восстановление за 1,9–2,5 с; процесс running |
| Security | UID 0 / write 200; UID 10001 / write 500; UID 10001 / write 200 |
| Networking | API 200 в обоих stages, proxy 502 → 200; Compose startup 1,4–7,3 с |
| Resources | OOMKilled=true, ExitCode=137, около 15 с |
| Reproducibility | Оба Dockerfile собраны, оба HTTP 200 |

Первая успешная сборка приложения с уже загруженными base images заняла 8,6 с;
сборки без изменений — около 1,1–1,4 с. Полный холодный старт с загрузкой образов
не имеет сопоставимого замера: Docker daemon дважды получил TLS timeout от GHCR.
Для этой проверки официальный uv image загружен через сеть хоста, SHA-256
manifest/config/layers проверены, затем образ импортирован в Docker. Dockerfile
сохраняют исходную ссылку `ghcr.io/astral-sh/uv:0.8.13`. Эти времена не обещают
идентичного результата на другой машине.

## Cleanup

В каждой стадии указан точный `docker rm -f <имя>` для созданного контейнера.
Для обоих Compose stages из их каталогов:

```bash
docker compose down -v --remove-orphans
```

Контейнеры `docker run --rm` удаляются сами. Учебные images можно оставить для
следующего запуска или удалить по конкретным тегам через `docker image rm`.
Общий `docker system prune` для этого воркшопа не нужен.

## За рамками

Практический Kubernetes (YAML, `kubectl`, manifests и т. п.), Swarm,
registry deployment, CI/CD, TLS, базы данных, ORM, миграции,
брокеры сообщений и production architecture. Презентация и конспект сюда не входят.
