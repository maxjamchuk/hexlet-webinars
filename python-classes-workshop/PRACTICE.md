# Практика для вебинара «Python: Классы»

Шесть коротких заданий занимают по 2–4 минуты. Для написания кода работайте в отдельной копии стадии по инструкции в [DEMO.md](DEMO.md); эталонные `models.py` уже содержат решения. В заданиях на предсказание сначала отвечайте в чате, затем запускайте пример.

## 1. Представления плейлиста — написание кода

**Стадия:** `01-representation`. **Время:** 3 минуты.

В копии `00-start/models.py` добавьте `Playlist.__str__` и `Playlist.__repr__`. Для `__str__` нужен вид `Post-Punk 80s — треков: 6`; число берите из `self._tracks`, поскольку `Playlist.__len__` ещё не появился. В `repr()` должны быть имя с `!r` и представление списка треков. Для полного вывода сначала добавьте `Track.__str__` и `Track.__repr__` по примеру эталона `01-representation/models.py`.

```python
playlist = create_playlist()  # из fixtures.py той же стадии
assert str(playlist) == "Post-Punk 80s — треков: 6"
assert "name='Post-Punk 80s'" in repr(playlist)
assert "Track(artist='The Cure'" in repr(playlist)
```

**Подсказка:** список сам вызывает `repr()` для каждого элемента; используйте `{self._tracks!r}`. Готовая реализация — в [стадии 01](01-representation/models.py).

## 2. Равенство композиций — написание кода

**Стадия:** `02-equality`. **Время:** 3 минуты.

В копии `01-representation/models.py` добавьте `Track.__eq__`. Сравнивайте три поля через кортежи. Если `other` не `Track` и не его подкласс, верните `NotImplemented`.

```python
first = Track("The Cure", "A Forest", 1980)
second = Track("The Cure", "A Forest", 1980)
assert first is not second
assert first == second
assert first != Track("The Cure", "A Forest", 1981)
assert first != "A Forest"
assert first.__eq__("A Forest") is NotImplemented
```

**Подсказка:** начните с `isinstance(other, Track)`, затем сравните `(artist, title, year)`. Готовая реализация — в [стадии 02](02-equality/models.py).

## 3. Длина и истинность — предсказание поведения

**Стадия:** `03-length`. **Время:** 2 минуты.

Посмотрите на `Playlist.__len__` в `03-length/models.py`. До запуска предскажите четыре результата. Нужно ли отдельно писать `__bool__`? Нужна ли длина отдельной композиции?

```python
playlist = create_playlist()
empty = Playlist("Empty", [])
print(len(playlist), len(empty), bool(playlist), bool(empty))
```

**Проверка:** записав ответ, запустите `python 03-length/demo.py` и сравните с выводом. **Подсказка:** когда `__bool__` не определён, Python может определить истинность по `__len__`. Готовая реализация — в [стадии 03](03-length/models.py).

## 4. Принадлежность — предсказание поведения

**Стадия:** `04-membership`. **Время:** 2 минуты.

Предскажите результаты до запуска. Оператор `in` сравнивает композиции как объекты `Track`; он не ищет строку в названии.

```python
playlist = create_playlist()
original = playlist._tracks[1]
copy = Track("The Cure", "A Forest", 1980)
other = Track("The Cure", "Other", 1980)
print(original in playlist, copy in playlist, other in playlist)
print("A Forest" in playlist, other not in playlist)
```

**Проверка:** `python 04-membership/demo.py`. **Подсказка:** `Track.__eq__` сравнивает значения полей, а `Playlist.__contains__` делегирует поиск списку. Готовая реализация — в [стадии 04](04-membership/models.py).

## 5. Индексы и срезы — написание кода

**Стадия:** `05-indexing`. **Время:** 3 минуты.

В копии `04-membership/models.py` добавьте `Playlist.__getitem__` одной делегирующей строкой. Проверьте первый и последний трек, срез и его тип. Не добавляйте `__iter__`.

```python
playlist = create_playlist()
assert playlist[0].title == "Love Will Tear Us Apart"
assert playlist[-1].title == "She's in Parties"
assert [track.title for track in playlist[1:3]] == ["A Forest", "Spellbound"]
assert isinstance(playlist[1:3], list)
assert len(list(playlist)) == 6  # неожиданная резервная итерация
```

**Подсказка:** верните результат `self._tracks[index]` без дополнительной обработки. Готовая реализация — в [стадии 05](05-indexing/models.py).

## 6. Исправление итератора — написание кода

**Стадия:** `06-iteration`. **Время:** 3 минуты.

Фрагмент ниже вызывает `TypeError`. Исправьте одну строку, чтобы `iter(playlist)` и `next()` работали. Плейлист должен оставаться итерируемым при повторном вызове `iter()`.

```python
class BrokenPlaylist:
    def __init__(self, tracks):
        self._tracks = list(tracks)

    def __iter__(self):
        return self._tracks  # исправьте

playlist = BrokenPlaylist(create_tracks())
iterator = iter(playlist)
assert next(iterator).title == "Love Will Tear Us Apart"
assert len(list(playlist)) == 6
```

**Подсказка:** список и итератор списка — разные объекты; используйте встроенную функцию `iter()`. Готовая реализация — в [стадии 06](06-iteration/models.py).
