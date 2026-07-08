# Рефакторинг к полиморфизму: убираем if/elif из render_task.
# Общий интерфейс: у каждого рендерера есть метод render(task).

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


class HtmlRenderer:
    def render(self, task):
        print(
            f"<p><b>{task['name']}</b> — {task['status']} "
            f"({task['executor']})</p>"
        )


# Функция не проверяет тип рендерера.
# Она просто вызывает render() — и каждый рендерер делает своё.
def render_task(task, renderer):
    renderer.render(task)


if __name__ == "__main__":
    renderers = [
        TextRenderer(),
        MarkdownRenderer(),
        HtmlRenderer(),
    ]

    for renderer in renderers:
        render_task(task, renderer)

    # Добавить новый формат = добавить новый класс.
    # Функцию render_task трогать не нужно.
