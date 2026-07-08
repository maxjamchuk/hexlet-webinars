# Плохой пример: функция знает слишком много форматов
# Проблема не в самом if/elif, а в том, что при добавлении
# нового формата нам придётся менять эту функцию.

task = {
    "name": "Исправить баг",
    "status": "В работе",
    "executor": "Анна",
}


def render_task(task, format_name):
    if format_name == "text":
        print(f"{task['name']} | {task['status']} | {task['executor']}")

    elif format_name == "markdown":
        print(f"**{task['name']}** — {task['status']} ({task['executor']})")

    elif format_name == "html":
        print(
            f"<p><b>{task['name']}</b> — {task['status']} "
            f"({task['executor']})</p>"
        )

    # Чтобы добавить "json", нужно прийти сюда и дописать ещё один elif.
    # Функция растёт и со временем становится трудно читаемой.


if __name__ == "__main__":
    render_task(task, "text")
    render_task(task, "markdown")
    render_task(task, "html")
