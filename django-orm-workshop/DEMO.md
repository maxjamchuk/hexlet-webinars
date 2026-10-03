# Шпаргалка преподавателя: Python / Django ORM

90 минут: блоки 0–4 ≈ 20 мин, 5–9 ≈ 25 мин, 10–12 ≈ 20 мин, 13–16 ≈ 25 мин.
120 минут: ещё 15 минут на блок 17 и 15 минут на вопросы/самостоятельный финальный запрос.
Команды выполняются из `django-orm-workshop`. Python-блоки — в одном `shell_plus`,
построчно или целиком; bash-блоки — в обычном терминале, не внутри Python.
Модели уже импортированы. Переходы к презентации обозначают темы, слайды здесь не создаются.

## 0. Reset / подготовка

Открыть: терминал, второй терминал для сервера, VS Code и браузер.
VS Code: `catalog/models.py`. Admin: войти перед занятием.

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runscript seed
uv run python manage.py shell_plus
```

Во втором терминале:

```bash
uv run python manage.py runserver
```

Admin: <http://127.0.0.1:8000/admin/>, `admin / workshop` (только локальное занятие).
Ожидание seed: **4 / 8 / 40 / 20 / 100** (publishers / series / comics / characters / reviews).
Фокус: reset заменяет весь каталог, пользователи сохраняются. После reset не использовать
старые экземпляры моделей и закэшированные QuerySet. Оставить обычный shell без `--print-sql`;
дополнительный режим можно показать позже.

## 1. Модель ↔ таблица

Открыть: презентация со связями → VS Code `catalog/models.py` → shell. Admin: не нужен.

```text
Publisher 1──N Series 1──N Comic N──M Character
                           │
                           1
                           │
                           N
                         Review
```

```python
Comic._meta.db_table  # 'catalog_comic'
Comic._meta.get_field("price").get_internal_type()  # 'DecimalField'
Comic._meta.get_field("series").column  # 'series_id'
Character.comics.through._meta.db_table  # 'catalog_character_comics'
```

Фокус: Python-поле соответствует столбцу; FK хранит ключ, M2M — отдельную таблицу.
Показать `UniqueConstraint`, проверки price/pages/rating и `related_name`.
`PositiveIntegerField` допускает 0, поэтому для страниц есть дополнительное `> 0`.
Валидацию вызывает `full_clean()`/Admin, а `save()` автоматически её не вызывает;
ограничения БД защищают данные и при `create()`/`update()`.

## 2. Первый QuerySet и Manager

Открыть: shell. VS Code / Admin: не нужны.

```python
type(Comic.objects).__name__  # 'Manager'
type(Comic.objects.all()).__name__  # 'QuerySet'
Comic.objects.all()  # preview коллекции, не все 40 строк
Comic.objects.first()  # #3 — A Blue Horizon
Comic.objects.last()  # #1 — Welcome to the Farm
Comic.objects.count()  # 40
```

Фокус: Manager — вход в запросы; QuerySet — описание выборки. `first()` / `last()`
учитывают `Meta.ordering` (здесь title, issue_number). Печать QuerySet в IPython
сама выполняет запрос для preview; для демонстрации ленивости не печатать `qs`.

## 3. get / filter / exclude / order_by / LIMIT

Открыть: shell. VS Code / Admin: не нужны.

```python
comic = Comic.objects.get(series__title="Batman", issue_number=1)
comic  # #1 — Gotham at Midnight
Comic.objects.filter(price__lt=5).count()  # 16
Comic.objects.filter(price__gte=10).count()  # 16
Comic.objects.filter(price__lt=10, pages__gte=30).count()  # 16
Comic.objects.exclude(series__publisher__name="Marvel Comics").count()  # 30
Comic.objects.order_by("-release_date")
latest = Comic.objects.order_by("-release_date", "series__title")[:5]
[(c.series.title, c.issue_number) for c in latest]
print(latest.query)
```

Ожидание `latest`: Amazing Spider-Man, Batman, Black Hammer, Hellboy, Invincible,
все #5; SQL содержит `ORDER BY` и `LIMIT 5`. Второй ключ сортировки устраняет
неопределённость при равных датах. Доступ к `series` пока делает дополнительные запросы.
Фокус: `get()` возвращает один объект, `filter()` — QuerySet; несколько kwargs означают AND.

```python
try:
    Comic.objects.get(series__title="Batman", issue_number=999)
except Comic.DoesNotExist:
    print("No such issue")

try:
    Comic.objects.get(series__title="Batman")
except Comic.MultipleObjectsReturned:
    print("More than one issue")
```

Ожидание: обе короткие строки, без traceback. Для отсутствующих/нескольких записей
`get()` не возвращает `None`/список.

## 4. Lookups

Открыть: shell. VS Code / Admin: не нужны.

```python
Comic.objects.filter(price__lte=5).count()  # 16
Comic.objects.filter(price__gt=10).count()  # 8
Comic.objects.filter(title__icontains="night").count()  # 3
Comic.objects.filter(release_date__year=2025).count()  # 16
Comic.objects.filter(series__title__in=["Batman", "X-Men"]).count()  # 10
empty = Comic.objects.filter(reviews__isnull=True)
[(c.series.title, c.issue_number) for c in empty.order_by("series__title")]
print(empty.query)
```

Ожидание `empty`: Amazing Spider-Man #4, Batman #3, Hellboy #3, Saga #4.
Фокус: `field__lookup`, traversal и преобразование даты; `isnull` на обратной связи
позволяет найти отсутствие отзывов (`LEFT OUTER JOIN … IS NULL`).

## 5. Ленивое выполнение и кэш

Открыть: shell. VS Code / Admin: не нужны. Выполнять по строке, не вводить отдельно `qs`.

```python
from django.db import connection, reset_queries

reset_queries()
qs = Comic.objects.filter(price__lt=10)
len(connection.queries)  # 0
print(qs.query)
len(connection.queries)  # 0 — печать SQL не выполняет запрос
list(qs)  # 24 объекта
len(connection.queries)  # 1
list(qs)
len(connection.queries)  # всё ещё 1
```

Фокус: построение запроса ≠ выполнение; повторная итерация того же QuerySet использует
кэш. Новое `Comic.objects.filter(...)` — новый QuerySet. `connection.queries` работает
здесь благодаря `DEBUG=True`; в тестах используем `CaptureQueriesContext`.
IPython preview `qs` вычисляет срез и не обязан заполнять кэш исходного QuerySet.

## 6. CRUD + Admin

Открыть: shell ↔ Admin / Comics. VS Code: не нужен.

```python
from datetime import date
from decimal import Decimal

series = Series.objects.get(title="Batman", publisher__name="DC Comics")
temporary = Comic.objects.create(
    series=series,
    issue_number=999,
    title="Workshop CRUD Special",
    release_date=date(2026, 4, 1),
    price=Decimal("5.00"),
    pages=32,
)
Comic.objects.count()  # 41
```

В Admin найти `Workshop CRUD Special`, открыть форму: цена 5.00.

```python
temporary.price = Decimal("6.00")
temporary.save(update_fields=["price"])
temporary.refresh_from_db()
temporary.price  # Decimal('6.00')
```

Обновить страницу Admin: цена 6.00. Затем:

```python
temporary.delete()  # удалён один Comic
Comic.objects.count()  # 40
```

Обновить список Admin: временный выпуск исчез. Фокус: INSERT → UPDATE → DELETE;
`Decimal` для денег, существующая серия для FK. Выпуск #999 зарезервирован для этого
примера; если прервали его посередине, выполните reset и начните заново.

## 7. ForeignKey и traversal через две связи

Открыть: презентация со связями → shell. VS Code: показать FK при необходимости. Admin: не нужен.

```python
comic = Comic.objects.get(series__title="Batman", issue_number=1)
comic.series  # Batman
comic.series.publisher  # DC Comics
qs = Comic.objects.filter(series__publisher__name="Marvel Comics")
qs.count()  # 10
print(qs.query)
```

Фокус: `__` описывает проход по связям в запросе; SQL содержит два JOIN.
Вызов `comic.series.publisher` при выводе — отдельный вопрос загрузки объектов,
который разберём в N+1.

## 8. Обратные связи

Открыть: shell. VS Code: показать `related_name` в моделях. Admin: не нужен.

```python
series = Series.objects.get(title="Batman")
series.comics.all()  # 5 выпусков
publisher = Publisher.objects.get(name="DC Comics")
publisher.series.all()  # Batman, Watchmen
comic = Comic.objects.get(series__title="Batman", issue_number=1)
comic.reviews.all()  # Alice: 5, Boris: 4, Charlie: 3
```

Фокус: вместо стандартного `_set` используются понятные имена `comics`, `series`, `reviews`.
С обратной стороны FK доступен менеджер коллекции.

## 9. ManyToMany в обе стороны

Открыть: shell ↔ Admin / Characters / Catwoman. VS Code: `Character.comics`.

```python
comic = Comic.objects.get(series__title="Batman", issue_number=1)
comic.characters.all()  # Batman, Joker
character = Character.objects.get(name="Batman")
character.comics.all()  # все 5 Batman
Comic.objects.filter(characters__name="Batman").count()  # 5
catwoman = Character.objects.get(name="Catwoman")
comic.characters.filter(name="Catwoman").exists()  # False
comic.characters.add(catwoman)
comic.characters.filter(name="Catwoman").exists()  # True
```

В seed **у Batman #1 нет связи с Catwoman**. В Admin обновить форму Catwoman:
`#1 — Gotham at Midnight` появился в выбранных выпусках. Затем восстановить данные:

```python
comic.characters.remove(catwoman)
comic.characters.filter(name="Catwoman").exists()  # False
```

Фокус: `add/remove` меняют промежуточную таблицу, сам персонаж не удаляется;
дополнительный `comic.save()` не требуется.

## 10. aggregate(): один результат для всей выборки

Открыть: shell. VS Code / Admin: не нужны.

```python
from django.db.models import Avg, Count

Review.objects.aggregate(average_rating=Avg("rating"))
Review.objects.aggregate(reviews_count=Count("id"), average_rating=Avg("rating"))
```

Ожидание: `{'average_rating': 3.94}`, затем
`{'reviews_count': 100, 'average_rating': 3.94}`.
Фокус: `aggregate()` сразу выполняет запрос и возвращает словарь, не QuerySet.

## 11. annotate(): результат на каждый выпуск

Открыть: shell. VS Code / Admin: не нужны.

```python
qs = Comic.objects.annotate(
    reviews_count=Count("reviews"),
    average_rating=Avg("reviews__rating"),
)
empty_comic = qs.get(series__title="Batman", issue_number=3)
empty_comic.reviews_count  # 0
empty_comic.average_rating is None  # True
qs = qs.filter(reviews_count__gte=3).order_by("-average_rating", "title")
print(qs.query)
[(c.title, c.reviews_count, round(c.average_rating, 2)) for c in qs[:5]]
```

Ожидание: A New Class (4, 4.75), Dawn over Gotham (3, 4.67), Goblin Night (3, 4.67),
The Long Way Home (3, 4.67), A Hero's Promise (4, 4.50).
SQL содержит `GROUP BY` и `HAVING`.
Фокус: `annotate` добавляет вычисляемые атрибуты экземплярам, не столбцы таблице;
фильтр агрегата сопоставить с HAVING. Для выпуска без отзывов Count = 0, Avg = NULL.

## 12. transaction.atomic(): три записи вместе

Открыть: VS Code `catalog/scripts/transaction_demo.py` → обычный терминал → Admin.

```bash
uv run python manage.py runscript transaction_demo --script-args rollback
```

Ожидание: `Transaction rolled back.`, затем Comic / Review / Character relation exists —
все `False`. В Admin поиск `Workshop Transaction Special` не даёт результатов.

```bash
uv run python manage.py runscript transaction_demo --script-args commit
```

Ожидание: `Transaction committed.`, все три проверки `True`.
В Admin есть Batman #1000, отзыв Workshop Reader и связь с Batman. В каталоге теперь 41 выпуск.
Показать границы `with transaction.atomic()` и исключение **внутри** блока;
оно перехватывается **снаружи**. Предыдущая демонстрационная запись удаляется до блока.

Перед следующим разделом обязательно вернуть 40 выпусков:

```bash
uv run python manage.py runscript seed
```

Фокус: atomic охватывает Comic, M2M-строку и Review; откатывается весь набор изменений.

## 13. N+1: измерение реальных запросов

Открыть: презентация N+1 → shell; VS Code: `catalog/scripts/n_plus_one.py`. Admin: не нужен.
Нужна baseline-база из 40 выпусков. Каждый замер начинается с нового QuerySet.

```python
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as queries:
    comics = Comic.objects.all()
    for comic in comics:
        publisher_name = comic.series.publisher.name

print(len(comics), len(queries))  # 40 81
print(queries[0]["sql"])  # только первый SQL

with CaptureQueriesContext(connection) as queries:
    comics = Comic.objects.all()
    for comic in comics:
        characters = list(comic.characters.all())

print(len(comics), len(queries))  # 40 41
```

Эквивалентный готовый сценарий в обычном терминале:

```bash
uv run python manage.py runscript n_plus_one
```

Фокус: 1+40+40 для двух FK и 1+40 для M2M. Один и тот же Series у разных экземпляров
Comic не создаёт общего кэша связанных объектов. `__str__()` здесь не вызывает SQL.
Не печатать QuerySet до замера и не выполнять `count()` внутри измеряемого блока.

## 14. select_related()

Открыть: shell. VS Code: `catalog/scripts/optimized_queries.py`. Admin: не нужен.

```python
with CaptureQueriesContext(connection) as queries:
    comics = Comic.objects.select_related("series__publisher")
    for comic in comics:
        publisher_name = comic.series.publisher.name

print(len(comics), len(queries))  # 40 1
print(comics.query)
```

Фокус: JOIN загружает поля Comic + Series + Publisher одним запросом.
Это загрузка одиночных связей (FK/OneToOne), а не коллекций M2M.

## 15. prefetch_related()

Открыть: shell. VS Code: тот же `optimized_queries.py`. Admin: не нужен.

```python
with CaptureQueriesContext(connection) as queries:
    comics = Comic.objects.prefetch_related("characters")
    for comic in comics:
        characters = list(comic.characters.all())

print(len(comics), len(queries))  # 40 2
print(queries[1]["sql"])  # отдельный запрос персонажей с IN
```

Готовые обе оптимизированные версии в терминале:

```bash
uv run python manage.py runscript optimized_queries
```

Фокус: 1 запрос выпусков + 1 запрос персонажей, объединение в Python.
Для использования кэша обращаться к `.characters.all()`; новый `.filter()` по связи
сделает другой запрос. `.query` основного QuerySet не показывает дополнительный prefetch SQL.

## 16. Финальный запрос

Открыть: презентация с задачей → shell. VS Code / Admin: не нужны.
Задача: Marvel, ≥3 отзывов, средний ≥4, порядок по убыванию среднего;
вывести серию/издательство и персонажей без N+1.

```python
from django.db.models import Avg, Count

comics = (
    Comic.objects.filter(series__publisher__name="Marvel Comics")
    .annotate(
        reviews_count=Count("reviews"),
        average_rating=Avg("reviews__rating"),
    )
    .filter(reviews_count__gte=3, average_rating__gte=4)
    .select_related("series__publisher")
    .prefetch_related("characters")
    .order_by("-average_rating")
)
print(comics.query)

with CaptureQueriesContext(connection) as queries:
    for comic in comics:
        print(
            comic.series.title,
            f"#{comic.issue_number}",
            comic.series.publisher.name,
            f"{comic.average_rating:.2f}",
            [character.name for character in comic.characters.all()],
        )

print("Queries:", len(queries))  # 2
```

Ожидание, строго в таком порядке (издательство везде Marvel Comics):

| Выпуск | Средний | Персонажи |
|---|---:|---|
| X-Men #1 | 4.75 | Cyclops, Storm, Wolverine |
| Amazing Spider-Man #3 | 4.67 | Green Goblin, Mary Jane, Spider-Man |
| Amazing Spider-Man #1 | 4.50 | Mary Jane, Spider-Man |
| X-Men #3 | 4.00 | Cyclops, Wolverine |

Фокус: WHERE + JOIN + GROUP BY + HAVING + ORDER BY, затем отдельный prefetch.
Не округлять среднее перед фильтрацией: 4.67 — формат вывода 14/3.
Для повторного замера заново выполнить присваивание `comics = (...)`.

## 17. Факультатив: Q / F / values (120 минут)

Открыть: shell. VS Code / Admin: не нужны. Отдельных scripts для этого блока нет.

`Q`: OR между условиями.

```python
from django.db.models import Q

Comic.objects.filter(Q(title__icontains="night") | Q(title__icontains="dark")).count()  # 5
```

`F`: арифметика в БД на временном выпуске. Создать его заново, поскольку CRUD-блок
свой объект уже удалил:

```python
from datetime import date
from decimal import Decimal
from django.db.models import F

temporary = Comic.objects.create(
    series=Series.objects.get(title="Batman", publisher__name="DC Comics"),
    issue_number=999,
    title="Workshop F Special",
    release_date=date(2026, 4, 1),
    price=Decimal("5.00"),
    pages=32,
)
Comic.objects.filter(series__title="Batman", issue_number=999).update(price=F("price") + 1)  # 1
temporary.refresh_from_db()
temporary.price  # Decimal('6.00')
temporary.delete()
Comic.objects.count()  # 40
```

Фокус: `update()` возвращает количество обновлённых строк; экземпляр в памяти
нужно обновить через `refresh_from_db()`. Цены исходных 40 выпусков не изменены.

`values()`: выбрать столбцы и получить словари.

```python
rows = Comic.objects.values("title", "series__title", "series__publisher__name")
list(rows.order_by("series__title", "issue_number")[:2])
```

Ожидание: два словаря Amazing Spider-Man — Webs over Queens и The Bridge Chase,
издательство Marvel Comics. Фокус: результат содержит выбранные поля, не экземпляры Comic.
