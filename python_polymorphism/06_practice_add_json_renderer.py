# Практика: добавьте JsonRenderer.
# Функцию render_task менять не нужно.

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


# TODO: добавьте класс JsonRenderer с методом render(task).
# Метод должен возвращать строку в формате JSON без использования модуля json.
# Пример возвращаемой строки:
# {"name": "Исправить баг", "status": "В работе", "executor": "Анна"}


def render_task(task, renderer):
    return renderer.render(task)


if __name__ == "__main__":
    renderers = [
        TextRenderer(),
        MarkdownRenderer(),
        # TODO: добавьте JsonRenderer() в этот список.
    ]

    for renderer in renderers:
        print(render_task(task, renderer))
