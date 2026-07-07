# Python: `functools`

Материалы к практическому воркшопу про модуль стандартной библиотеки `functools`.

`functools` помогает работать с функциями как с объектами: писать корректные декораторы, кэшировать повторные вычисления, заранее фиксировать аргументы и выбирать поведение функции в зависимости от типа данных.

## Презентация

[Открыть презентацию в Google Slides](https://docs.google.com/presentation/d/1n136u_wGchCz40RVCgvAGiYS06MR3ze67jfm3dhkIio/edit)

## Для кого

Воркшоп будет полезен, если вы уже:

- понимаете, как работают функции в Python;
- умеете передавать аргументы в функции;
- знакомы с `*args` и `**kwargs`;
- видели декораторы;
- хотите лучше понимать, что происходит с функцией после обёртки;
- сталкивались с повторяющимися или медленными вычислениями.

## Что разбираем

На воркшопе разбираются инструменты из `functools`, которые часто встречаются в реальном Python-коде:

- `wraps` — сохранение имени, документации и метаданных функции при написании декораторов;
- `cache` — простой кэш без ограничения размера;
- `lru_cache` — кэш с ограничением размера;
- `partial` — создание новой функции с заранее заданными аргументами;
- `reduce` — свёртка последовательности в одно значение;
- `singledispatch` — выбор реализации функции по типу первого аргумента.

## Основная идея

В Python функции — это полноценные объекты.

Функцию можно:

- сохранить в переменную;
- передать в другую функцию;
- вернуть из функции;
- обернуть декоратором;
- дополнительно настроить;
- закэшировать;
- использовать как часть более сложной логики.

`functools` даёт готовые инструменты для таких задач, чтобы не писать всё вручную.

## План воркшопа

Примерный план:

1. Коротко вспоминаем, что функции — это объекты.
2. Разбираем проблему декораторов без `wraps`.
3. Чиним декоратор с помощью `functools.wraps`.
4. Разбираем кэширование через `cache` и `lru_cache`.
5. Сравниваем выполнение функции до и после кэша.
6. Используем `partial` для заранее настроенных функций.
7. Обсуждаем, когда `partial` улучшает читаемость, а когда мешает.
8. Коротко смотрим на `reduce`.
9. Коротко смотрим на `singledispatch`.
10. Подводим итоги и обсуждаем вопросы.

## Практика

Во время воркшопа можно выполнить несколько небольших заданий.

### 1. Починить декоратор

Есть декоратор `timer`, который измеряет время выполнения функции.

Проблема: без `wraps` после декорирования функция теряет нормальные метаданные.

Нужно сделать так, чтобы сохранялись:

- имя функции;
- docstring;
- нормальное отображение в `help()`;
- удобная отладка.

Пример проверки:

```python
print(greet.__name__)
print(greet.__doc__)
help(greet)
```

### 2. Добавить кэш

Есть функция, которая выполняет повторяющиеся вычисления.

Нужно добавить кэширование:

```python
from functools import cache
```

или:

```python
from functools import lru_cache
```

После этого можно сравнить время выполнения:

```python
from time import perf_counter

t0 = perf_counter()
result = fib(35)
print("took", perf_counter() - t0)
```

### 3. Сделать функцию через `partial`

Нужно взять функцию с несколькими аргументами и заранее зафиксировать часть настроек.

Например:

```python
import json
from functools import partial

dump_pretty = partial(
    json.dumps,
    ensure_ascii=False,
    indent=2,
)
```

Теперь `dump_pretty()` можно использовать как готовую настроенную функцию.

### 4. Разобрать `reduce`

`reduce` сворачивает последовательность значений в один результат.

Пример:

```python
from functools import reduce

numbers = [1, 2, 3, 4]

product = reduce(lambda acc, x: acc * x, numbers, 1)

print(product)
# 24
```

Важно: `reduce` не всегда делает код понятнее. Иногда лучше использовать обычный цикл, `sum`, `max`, `min` или `join`.

### 5. Посмотреть `singledispatch`

`singledispatch` позволяет описать одну функцию с разной реализацией для разных типов.

```python
from functools import singledispatch

@singledispatch
def normalize(value):
    return str(value)

@normalize.register
def _(value: str):
    return value.strip().lower()
```

Это удобно, когда есть одна общая операция, но входные данные могут быть разных типов.

## Как запустить примеры

Для работы достаточно установленного Python 3.

Проверить версию:

```bash
python --version
```

Запустить файл:

```bash
python example.py
```

Или открыть интерактивный режим:

```bash
python
```

## Полезные импорты

```python
from functools import (
    wraps,
    cache,
    lru_cache,
    partial,
    reduce,
    singledispatch,
)
```

## Мини-шпаргалка

### `wraps`

Используется внутри декоратора:

```python
from functools import wraps

def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
```

### `cache`

Кэширует результат функции:

```python
from functools import cache

@cache
def fib(n):
    if n < 2:
        return n

    return fib(n - 1) + fib(n - 2)
```

### `lru_cache`

Кэширует результат, но ограничивает размер кэша:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive(value):
    return value * value
```

### `partial`

Создаёт новую функцию с частью заранее заданных аргументов:

```python
from functools import partial

parse_hex = partial(int, base=16)

print(parse_hex("ff"))
# 255
```

### `reduce`

Сворачивает последовательность в одно значение:

```python
from functools import reduce

result = reduce(lambda acc, x: acc + x, [1, 2, 3], 0)
```

### `singledispatch`

Выбирает реализацию по типу аргумента:

```python
from functools import singledispatch

@singledispatch
def render(value):
    return str(value)

@render.register
def _(value: list):
    return ", ".join(map(str, value))
```

## На что обратить внимание

- `wraps` почти всегда нужен, если вы пишете свой декоратор.
- Декоратор должен возвращать результат вызова исходной функции.
- Кэшировать стоит только функции, которые при одинаковых аргументах возвращают одинаковый результат.
- Аргументы кэшируемой функции должны быть hashable.
- `cache` может бесконтрольно расти, если у функции много разных входных данных.
- `lru_cache(maxsize=...)` помогает ограничить рост кэша.
- `partial` полезен, когда заранее заданные аргументы делают код понятнее.
- `reduce` стоит использовать осторожно: он часто менее читаемый, чем обычный цикл.
- `singledispatch` удобен для простых случаев, но не должен заменять нормальную архитектуру приложения.

## Когда это пригодится

`functools` полезен, когда нужно:

- написать свой декоратор;
- сохранить метаданные функции после декорирования;
- ускорить повторные вычисления;
- убрать повторяющиеся аргументы из вызовов;
- заранее настроить функцию под конкретный сценарий;
- аккуратно обработать разные типы входных данных;
- лучше понимать чужой Python-код.

## Полезные ссылки

- [`functools` в документации Python](https://docs.python.org/3/library/functools.html)
- [`functools.wraps`](https://docs.python.org/3/library/functools.html#functools.wraps)
- [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache)
- [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial)
- [`functools.reduce`](https://docs.python.org/3/library/functools.html#functools.reduce)
- [`functools.singledispatch`](https://docs.python.org/3/library/functools.html#functools.singledispatch)

## Статус материалов

Материалы можно дорабатывать: добавлять примеры, практические задания, решения и дополнительные заметки после проведения воркшопа.