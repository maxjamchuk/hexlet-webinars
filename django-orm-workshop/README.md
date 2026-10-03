# Python: Django ORM — Comic Catalog

Учебный проект для live coding на 90–120 минут. Основной интерфейс — IPython
через `shell_plus`; Django Admin показывает состояние БД. Маршрут преподавателя:
[DEMO.md](DEMO.md).

## Быстрый запуск

Нужен [uv](https://docs.astral.sh/uv/getting-started/installation/) и Python ≥ 3.12.
Файл `.python-version` выбирает Python 3.12; при необходимости `uv` скачает его.
Все команды ниже выполняются из этой папки:

```bash
cd django-orm-workshop
uv sync
uv run python manage.py migrate
uv run python manage.py runscript seed
uv run python manage.py shell_plus
```

Проверенная среда: Python **3.12.12**, Django **5.2.17**, django-extensions **4.1**,
IPython **9.17.1**. Выбрана поддерживаемая ветка
[Django 5.2 LTS](https://www.djangoproject.com/download/#supported-versions),
совместимая с Python 3.12. Точные версии всех зависимостей — в `uv.lock`.
Для установки строго по lock-файлу можно выполнить `uv sync --locked`.

## Shell и SQL

```bash
uv run python manage.py shell_plus
uv run python manage.py shell_plus --print-sql
```

Модели `Publisher`, `Series`, `Comic`, `Character`, `Review` импортируются автоматически.
Вторая команда проверена: выводит SQL при выполнении запросов
([документация shell_plus](https://django-extensions.readthedocs.io/en/latest/shell_plus.html#sql-queries)).
Для основного занятия достаточно обычного shell и `print(qs.query)`:

```python
qs = Comic.objects.filter(series__publisher__name="Marvel Comics")
print(qs.query)
```

`.query` показывает структуру SQL, не выполняя его. Это отладочное представление,
а не готовая SQL-строка с корректно процитированными параметрами для копирования в БД.
Для подсчёта выполненных запросов используются `CaptureQueriesContext` либо
`connection.queries` при включённом `DEBUG`. Здесь `DEBUG=True`.

## Django Admin

В отдельном терминале:

```bash
uv run python manage.py runserver
```

Откройте <http://127.0.0.1:8000/admin/>. Логин: **admin**, пароль: **workshop**.

Эти credentials предназначены исключительно для локального workshop-проекта
и не являются примером production-конфигурации. Настройки проекта также локальные.

Seed создаёт этого пользователя только при его отсутствии. Существующие пользователи,
пароли и права не меняются. Если `admin` уже был создан с другим паролем, используйте
его пароль или `uv run python manage.py changepassword admin`.

Все пять моделей зарегистрированы. В Comics поиск `Batman`, `X-Men` или `Spider-Man`
найдёт серию; доступны фильтры по издательству, серии и дате. У Characters есть
двухколоночный редактор связей с выпусками.

## Данные и reset

```bash
uv run python manage.py runscript seed
```

Команда **полностью заменяет содержимое каталога**, включая изменения из shell/Admin,
одной атомарной операцией. Django users остаются. При ошибке восстанавливается
состояние каталога до запуска. `db.sqlite3` не хранится в Git; источник данных —
[catalog/demo_data.py](catalog/demo_data.py). После reset создавайте новые QuerySet:
ранее загруженные Python-объекты и их кэши сами не обновляются.

| Объекты | Количество |
|---|---:|
| Publisher | 4 |
| Series | 8 |
| Comic | 40 |
| Character | 20 |
| Review | 100 |

Издательства: DC Comics, Marvel Comics, Image Comics, Dark Horse Comics.
У каждого две серии, у каждой серии пять выпусков. Названия, даты, цены, состав
персонажей и отзывы — **учебные данные, не библиографически точные сведения**.

У выпусков 0–4 отзыва с оценками 1–5; четыре выпуска без отзывов. У 39 из 40 выпусков
несколько персонажей. Для предсказуемых lookups все серии используют одинаковые
даты/цены/страницы по номеру выпуска; цены: 3.99, 4.99, 6.50, 10.00, 12.50.
Деньги создаются через `Decimal`, данные не используют случайность или фиксированные ID.

Финальный запрос из DEMO возвращает только:

| Выпуск | Отзывов | Средний рейтинг |
|---|---:|---:|
| X-Men #1 | 4 | 4.75 |
| Amazing Spider-Man #3 | 3 | 4.666… |
| Amazing Spider-Man #1 | 4 | 4.50 |
| X-Men #3 | 3 | 4.00 |

Загрузка результата вместе с series/publisher и characters занимает **2 SQL-запроса**.

## Готовые демонстрации

```bash
uv run python manage.py runscript transaction_demo --script-args rollback
uv run python manage.py runscript transaction_demo --script-args commit
uv run python manage.py runscript seed
uv run python manage.py runscript n_plus_one
uv run python manage.py runscript optimized_queries
```

Transaction demo создаёт `Batman #1000 — Workshop Transaction Special`, связь с Batman
и отзыв. В режиме rollback все три записи откатываются; commit оставляет 41 выпуск
и 101 отзыв. Перед следующим запуском transaction demo удаляет свой предыдущий
результат **до** демонстрируемой транзакции. Поэтому повторные commit и rollback
после commit безопасны. `seed` перед N+1 возвращает исходные 40 выпусков.

| Доступ к отношениям на 40 выпусках | SQL-запросов |
|---|---:|
| `comic.series.publisher.name` | 81 |
| То же с `select_related("series__publisher")` | 1 |
| `list(comic.characters.all())` | 41 |
| То же с `prefetch_related("characters")` | 2 |

Скрипты измеряют реальные запросы, а не печатают заготовленные числа. У каждого
замера новый QuerySet; `__str__()` всех моделей использует только собственные поля.
Без reset числа зависят от текущего количества выпусков: для N штук — 1+2N и 1+N.

## Проверки

```bash
uv run pytest
uv run ruff check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

Тесты проверяют ограничения и валидацию, связи, полный логический результат повторного
seed, сохранность пользователей, атомарность при сбое, финальный запрос, ленивость,
точные SQL counts, реальные commit/rollback, shell_plus и работу Admin.
Pytest использует отдельную тестовую БД и не изменяет локальный `db.sqlite3`.

## Структура

```text
django-orm-workshop/
├── .gitignore
├── .python-version
├── README.md
├── DEMO.md
├── pyproject.toml
├── uv.lock
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── catalog/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── admin.py
│   ├── demo_data.py
│   ├── migrations/       # 0001_initial.py + __init__.py
│   ├── scripts/          # seed, transaction_demo, n_plus_one, optimized_queries
│   └── tests/            # models, seed, queries, transactions, admin, demo flow
└── db.sqlite3            # создаётся локально, игнорируется Git
```
