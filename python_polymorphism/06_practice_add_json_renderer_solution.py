# Решение практики: JsonRenderer добавлен как новый класс.
# Функция render_task не изменилась.

task = {
    "name": "Исправить баг",
    "status": "В работе",
    "executor": "Анна",
}


class TextRenderer:
    def render(self, task):
        print(f"{task['name']} | {task['status']} | {task['executor']}")


class MarkdownRenderer:
    def render(self, task):
        print(f"**{task['name']}** — {task['status']} ({task['executor']})")


class JsonRenderer:
    def render(self, task):
        # Собираем строку вручную, без модуля json.
        result = (
            f'{{"name": "{task["name"]}", '
            f'"status": "{task["status"]}", '
            f'"executor": "{task["executor"]}"}}'
        )
        print(result)


def render_task(task, renderer):
    renderer.render(task)


if __name__ == "__main__":
    renderers = [
        TextRenderer(),
        MarkdownRenderer(),
        JsonRenderer(),
    ]

    for renderer in renderers:
        render_task(task, renderer)
