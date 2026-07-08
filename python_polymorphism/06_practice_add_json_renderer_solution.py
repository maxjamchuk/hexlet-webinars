# Решение практики: JsonRenderer добавлен как новый класс.
# Функция render_task не изменилась.

task = {
    "name": "Исправить баг",
    "status": "В работе",
    "executor": "Анна",
}


class TextRenderer:
    def render(self, task):
        return f"{task['name']} | {task['status']} | {task['executor']}"


class MarkdownRenderer:
    def render(self, task):
        return f"**{task['name']}** — {task['status']} ({task['executor']})"


class JsonRenderer:
    def render(self, task):
        # Собираем строку вручную, без модуля json.
        return (
            f'{{"name": "{task["name"]}", '
            f'"status": "{task["status"]}", '
            f'"executor": "{task["executor"]}"}}'
        )


def render_task(task, renderer):
    return renderer.render(task)


if __name__ == "__main__":
    renderers = [
        TextRenderer(),
        MarkdownRenderer(),
        JsonRenderer(),
    ]

    for renderer in renderers:
        print(render_task(task, renderer))
