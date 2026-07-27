import json
from pathlib import Path
from typing import Any


class TaskRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def get_all(self) -> list[dict[str, Any]]:
        with self.path.open(encoding="utf-8") as file:
            return json.load(file)

    def find_by_id(self, task_id: int) -> dict[str, Any] | None:
        return next(
            (task for task in self.get_all() if task["id"] == task_id),
            None,
        )

    def add(self, task: dict[str, Any]) -> dict[str, Any]:
        tasks = self.get_all()
        tasks.append(task)
        self._save(tasks)
        return task

    def update(
        self,
        task_id: int,
        changes: dict[str, Any],
    ) -> dict[str, Any] | None:
        tasks = self.get_all()

        for task in tasks:
            if task["id"] == task_id:
                task.update(changes)
                self._save(tasks)
                return task

        return None

    def delete(self, task_id: int) -> bool:
        tasks = self.get_all()
        remaining_tasks = [task for task in tasks if task["id"] != task_id]

        if len(remaining_tasks) == len(tasks):
            return False

        self._save(remaining_tasks)
        return True

    def _save(self, tasks: list[dict[str, Any]]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(tasks, file, ensure_ascii=False, indent=2)
            file.write("\n")
