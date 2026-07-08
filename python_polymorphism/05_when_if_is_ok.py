# if/elif — не всегда проблема.
# Проблема начинается, когда одна функция накапливает много вариантов
# поведения и постоянно расширяется. Простые проверки — это нормально.

tasks = [
    {"name": "Исправить баг", "status": "В работе", "executor": "Анна"},
    {"name": "Написать тесты", "status": "Новая", "executor": "Иван"},
]

current_user = {"name": "Анна", "role": "admin"}


def show_task_count(tasks):
    # Простая проверка — здесь if уместен.
    if not tasks:
        print("Задач нет.")
    else:
        print(f"Задач: {len(tasks)}")


def get_greeting(user):
    # Выбор между двумя фиксированными вариантами — тоже нормально.
    if user["role"] == "admin":
        return f"Добро пожаловать, администратор {user['name']}!"
    return f"Добро пожаловать, {user['name']}!"


if __name__ == "__main__":
    show_task_count(tasks)
    show_task_count([])

    print(get_greeting(current_user))
    print(get_greeting({"name": "Иван", "role": "user"}))
