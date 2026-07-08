# Резерв: фильтрация задач через полиморфизм.
# Разные фильтры имеют общий метод match(task).

tasks = [
    {"name": "Исправить баг", "status": "В работе", "executor": "Анна", "label": "bug"},
    {"name": "Написать тесты", "status": "Новая", "executor": "Иван", "label": "test"},
    {"name": "Обновить README", "status": "Готово", "executor": "Анна", "label": "docs"},
]


class StatusFilter:
    def __init__(self, status):
        self.status = status

    def match(self, task):
        return task["status"] == self.status


class ExecutorFilter:
    def __init__(self, executor):
        self.executor = executor

    def match(self, task):
        return task["executor"] == self.executor


class LabelFilter:
    def __init__(self, label):
        self.label = label

    def match(self, task):
        return task["label"] == self.label


# Функция не знает, какой именно фильтр передан.
# Она просто вызывает match() — каждый фильтр решает сам.
def filter_tasks(tasks, task_filter):
    return [task for task in tasks if task_filter.match(task)]


if __name__ == "__main__":
    print("Задачи со статусом 'В работе':")
    for task in filter_tasks(tasks, StatusFilter("В работе")):
        print(f"  {task['name']}")

    print("\nЗадачи исполнителя 'Анна':")
    for task in filter_tasks(tasks, ExecutorFilter("Анна")):
        print(f"  {task['name']}")

    print("\nЗадачи с меткой 'test':")
    for task in filter_tasks(tasks, LabelFilter("test")):
        print(f"  {task['name']}")
