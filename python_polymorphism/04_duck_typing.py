# Утиная типизация: Python не спрашивает "кто ты?",
# а спрашивает "есть ли у тебя нужный метод?".

task = {
    "name": "Написать тесты",
    "status": "Новая",
    "executor": "Иван",
}


class TextRenderer:
    def render(self, task):
        print(f"{task['name']} | {task['status']} | {task['executor']}")


# У этого класса нет метода render — он "сломан".
class BrokenRenderer:
    pass


def render_task(task, renderer):
    renderer.render(task)


if __name__ == "__main__":
    # TextRenderer работает — у него есть render().
    render_task(task, TextRenderer())

    # BrokenRenderer не работает — Python обнаружит это только
    # в момент вызова, а не при создании объекта.
    try:
        render_task(task, BrokenRenderer())
    except AttributeError as e:
        print(f"Ошибка: {e}")
