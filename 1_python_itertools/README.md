# Python: `itertools`

Материалы к вебинару про модуль стандартной библиотеки `itertools`.

`itertools` помогает работать с итераторами: склеивать последовательности, брать части потока, группировать данные, строить комбинации и писать код без лишних временных списков.

## Презентация

[Открыть презентацию в Google Slides](https://docs.google.com/presentation/d/19VCflrPoQFB-7JH7CPvnkslpIHOyg6uI1zuCdYnuz9c/edit)

## Для кого

Вебинар будет полезен, если вы уже:

- уверенно пишете `for` и `while`;
- работаете со списками, словарями и кортежами;
- понимаете, что такое итерация;
- видели генераторы или генераторные выражения;
- хотите писать меньше вложенных циклов и меньше промежуточных списков.

## Что разбираем

На вебинаре разбираются основные инструменты `itertools`:

- `chain` — склеивание нескольких итерируемых объектов;
- `chain.from_iterable` — «расплющивание» вложенных последовательностей;
- `islice` — срезы для итераторов без превращения в список;
- `groupby` — группировка соседних элементов;
- `product` — декартово произведение;
- `combinations` — сочетания без повторов;
- `count`, `cycle`, `repeat` — бесконечные и повторяющиеся последовательности;
- `tee` — создание нескольких итераторов из одного;
- `pairwise` — работа с соседними элементами.

## Основная идея

Обычный код на циклах часто выглядит так:

```python
result = []

for group in groups:
    for item in group:
        if item > 0:
            result.append(item)
```

С `itertools` такие задачи можно собирать как pipeline:

```python
from itertools import chain, islice

items = chain.from_iterable(groups)
first_items = islice(items, 10)
```

Главная идея: данные проходят по шагам, а лишние списки не создаются без необходимости.

## Практика

Во время вебинара можно попробовать несколько небольших заданий:

1. Сделать `flatten` вложенного списка через `chain.from_iterable`.
2. Взять первые `N` элементов потока через `islice`.
3. Разбить данные на группы через `groupby`.
4. Сгенерировать варианты через `product`.
5. Получить уникальные пары через `combinations`.
6. Разобрать, почему некоторые итераторы нельзя пройти дважды.

## Как запустить примеры

Для работы достаточно установленного Python 3.

Проверить версию:

```bash
python --version
```

Запустить отдельный файл с примером:

```bash
python example.py
```

Или открыть Python REPL:

```bash
python
```

## Полезные импорты

```python
from itertools import (
    chain,
    islice,
    groupby,
    product,
    combinations,
    count,
    cycle,
    repeat,
    tee,
    pairwise,
)
```

## Примеры

Склеить несколько последовательностей:

```python
from itertools import chain

result = list(chain([1, 2], [3, 4], [5]))
print(result)
# [1, 2, 3, 4, 5]
```

«Расплющить» вложенный список:

```python
from itertools import chain

nested = [[1, 2], [3], [4, 5]]

result = list(chain.from_iterable(nested))
print(result)
# [1, 2, 3, 4, 5]
```

Взять первые элементы без создания полного списка:

```python
from itertools import islice

numbers = (x * x for x in range(1_000_000))

first_five = list(islice(numbers, 5))
print(first_five)
# [0, 1, 4, 9, 16]
```

Сгруппировать соседние элементы:

```python
from itertools import groupby

items = ["a", "a", "b", "b", "a"]

for key, group in groupby(items):
    print(key, list(group))

# a ['a', 'a']
# b ['b', 'b']
# a ['a']
```

Сгенерировать пары:

```python
from itertools import combinations

names = ["Ann", "Bob", "Chad"]

pairs = list(combinations(names, 2))
print(pairs)
# [('Ann', 'Bob'), ('Ann', 'Chad'), ('Bob', 'Chad')]
```

## На что обратить внимание

- Большинство функций `itertools` возвращают итераторы, а не списки.
- Итератор часто можно пройти только один раз.
- `islice` полезен, когда не нужно читать весь поток данных.
- `groupby` группирует только соседние элементы. Если нужно собрать все одинаковые значения вместе, данные обычно надо сначала отсортировать.
- `product`, `combinations` и `permutations` могут быстро создавать очень много вариантов.
- Не стоит бездумно делать `list(...)` вокруг больших или бесконечных итераторов.
- `tee` может незаметно копить данные в памяти, если один из созданных итераторов сильно отстаёт от другого.

## Когда это полезно

`itertools` хорошо подходит для задач, где нужно:

- обрабатывать данные потоком;
- не хранить всё в памяти сразу;
- заменить несколько вложенных циклов на более читаемый pipeline;
- сгенерировать варианты для тестов;
- обработать логи, события или последовательности;
- взять только первые `N` элементов большого набора данных.

## Полезные ссылки

- [`itertools` в документации Python](https://docs.python.org/3/library/itertools.html)
- [Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Recipes из документации `itertools`](https://docs.python.org/3/library/itertools.html#itertools-recipes)
- [`more-itertools`](https://pypi.org/project/more-itertools/)

## Статус материалов

Материалы можно дорабатывать: добавлять примеры, практические задания, решения и дополнительные рецепты после проведения вебинара.