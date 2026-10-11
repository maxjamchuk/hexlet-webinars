# Python: Классы

Учебный репозиторий для **90-минутного вебинара Hexlet**. Аудитория — студенты второго модуля Python, знакомые с классами и `__init__`. Цель — увидеть, как специальные методы подключают собственные объекты к привычным операциям Python: `print()`, `repr()`, `==`, `len()`, `bool()`, `in`, `[]` и `for`.

Сквозной пример — плейлист **Post-Punk 80s** из шести реальных композиций Joy Division, The Cure, Siouxsie and the Banshees, The Sound, The Chameleons и Bauhaus. `Track` описывает одну композицию; `Playlist` хранит собственную копию списка треков. Класс плейлиста не наследуется от `list`: он делегирует операции внутреннему списку и участвует в протоколах Python по своим методам.

## Подготовка

Нужен **Python 3.12 или новее**. Используется только стандартная библиотека. Установка пакетов для самого вебинара не нужна. Версия для `uv` указана в `.python-version`, а разрешённое окружение зафиксировано в `uv.lock`. Файл `uv.toml` направляет кэш `uv` в локальную игнорируемую папку `.uv-cache`.

Из каталога `python-classes-workshop` проверьте интерпретатор:

```shell
python --version
```

Без `uv`:

```shell
python 00-start/demo.py
python 05-indexing/demo.py
python -m unittest discover -s 05-indexing -p test_models.py -v
python tools/smoke_check.py
```

С `uv`:

```shell
uv sync --offline
uv run --offline python 00-start/demo.py
uv run --offline python -m unittest discover -s 05-indexing -p test_models.py -v
uv run --offline python tools/smoke_check.py
```

Параметр `--offline` достаточен после установки Python 3.12 через `uv`; если интерпретатор ещё не установлен, сначала выполните `uv python install 3.12` при доступной сети. Зависимостей проекта нет. Можно также запускать `uv run python ...` без `--offline`.

## Маршрут вебинара

Каждая стадия — самостоятельная папка с собственными `models.py`, `fixtures.py`, `demo.py`, `test_models.py` и `README.md`. Можно открыть любую стадию и сразу запустить её демонстрацию. Данные и порядок шести композиций одинаковы; новые методы появляются по одному шагу за раз.

| Время | Стадия | Что добавляется |
|---|---|---|
| 00:00–00:08 | [00-start](00-start/README.md) | Обычные конструкторы; недоступные операции |
| 00:08–00:22 | [01-representation](01-representation/README.md) | `__str__`, `__repr__` |
| 00:22–00:35 | [02-equality](02-equality/README.md) | `Track.__eq__`, `NotImplemented`, `is` и `==` |
| 00:35–00:47 | [03-length](03-length/README.md) | `Playlist.__len__`, истинность через длину |
| 00:47–00:59 | [04-membership](04-membership/README.md) | `Playlist.__contains__` |
| 00:59–01:11 | [05-indexing](05-indexing/README.md) | `Playlist.__getitem__`, срезы и резервная итерация |
| 01:11–01:22 | [06-iteration](06-iteration/README.md) | Явный `Playlist.__iter__` |
| 01:22–01:30 | [07-final](07-final/README.md) | Интеграция и выбор уместных методов |
| По возможности | [08-bonus-slots](08-bonus-slots/README.md) | `__dict__`, `__slots__` за 5–7 минут, если время сэкономлено внутри 90 минут |

## Команды

Любая демонстрация запускается из корня командой `python <stage>/demo.py`, например:

```shell
python 01-representation/demo.py
python 06-iteration/demo.py
python 08-bonus-slots/demo.py
```

Тесты одной стадии запускаются отдельно, чтобы одноимённые модули разных стадий не смешивались:

```shell
python -m unittest discover -s 01-representation -p test_models.py -v
python -m unittest discover -s 08-bonus-slots -p test_models.py -v
```

Все демо и тесты в отдельных процессах, с правильной рабочей директорией, проверяет одна команда:

```shell
python tools/smoke_check.py
```

См. [пошаговый сценарий преподавателя](DEMO.md), [шесть коротких заданий](PRACTICE.md) и [решения с разбором](SOLUTIONS.md). Факультативная стадия `08` независима от основной последовательности и не добавляет обязательное время сверх 90 минут.
