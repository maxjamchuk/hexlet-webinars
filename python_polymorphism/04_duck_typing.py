# Утиная типизация: Python не требует общего родителя или конкретного типа.
# Он просто пытается вызвать нужный метод в момент выполнения.

task = {
    "name": "Написать тесты",
    "status": "Новая",
    "executor": "Иван",
}


class TextRenderer:
    def render(self, task):
        return f"{task['name']} | {task['status']} | {task['executor']}"


# У этого класса нет метода render — он "сломан".
class BrokenRenderer:
    pass


def render_task(task, renderer):
    return renderer.render(task)


if __name__ == "__main__":
    # TextRenderer работает — у него есть render().
    print(render_task(task, TextRenderer()))

    # BrokenRenderer не работает — Python обнаружит это только
    # в момент вызова, а не при создании объекта.
    try:
        print(render_task(task, BrokenRenderer()))
    except AttributeError as e:
        print(f"Ошибка: {e}")
