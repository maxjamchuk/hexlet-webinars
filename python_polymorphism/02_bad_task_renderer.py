# Плохой пример: функция знает слишком много форматов.
# Чтобы добавить новый формат, нужно менять эту функцию
# и дописывать новую ветку elif — она растёт вместе с числом форматов.

task = {
    "name": "Исправить баг",
    "status": "В работе",
    "executor": "Анна",
}


def render_task(task, format_name):
    if format_name == "text":
        return f"{task['name']} | {task['status']} | {task['executor']}"

    elif format_name == "markdown":
        return f"**{task['name']}** — {task['status']} ({task['executor']})"

    elif format_name == "html":
        return (
            f"<p><b>{task['name']}</b> — {task['status']} "
            f"({task['executor']})</p>"
        )

    # Неизвестный формат — явно сообщаем об ошибке.
    raise ValueError(f"Неизвестный формат: {format_name}")


if __name__ == "__main__":
    print(render_task(task, "text"))
    print(render_task(task, "markdown"))
    print(render_task(task, "html"))

    # Попытка передать неизвестный формат.
    try:
        print(render_task(task, "json"))
    except ValueError as error:
        print(f"Ошибка: {error}")
