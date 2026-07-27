from typing import Any

from .notifications import NotificationClient, NotificationError
from .repository import TaskRepository


class ValidationError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        notification_client: NotificationClient | None = None,
    ) -> None:
        self.repository = repository
        self.notification_client = notification_client

    def get_all(self) -> list[dict[str, Any]]:
        return self.repository.get_all()

    def get_by_id(self, task_id: int) -> dict[str, Any]:
        task = self.repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    def create(self, data: Any) -> dict[str, Any]:
        self._validate_payload(data, allowed_fields={"title", "completed"})

        if "title" not in data:
            raise ValidationError("title is required")

        title = self._validate_title(data["title"])
        completed = self._validate_completed(data.get("completed", False))
        tasks = self.repository.get_all()
        next_id = max((task["id"] for task in tasks), default=0) + 1

        task = {
            "id": next_id,
            "title": title,
            "completed": completed,
        }
        return self.repository.add(task)

    def update(self, task_id: int, data: Any) -> dict[str, Any]:
        self._validate_payload(
            data,
            allowed_fields={"title", "completed"},
            allow_empty=False,
        )

        changes: dict[str, Any] = {}
        if "title" in data:
            changes["title"] = self._validate_title(data["title"])
        if "completed" in data:
            changes["completed"] = self._validate_completed(data["completed"])

        current_task = self.repository.find_by_id(task_id)
        if current_task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")

        task = self.repository.update(task_id, changes)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")

        became_completed = (
            current_task["completed"] is False
            and changes.get("completed") is True
        )
        if became_completed and self.notification_client is not None:
            try:
                self.notification_client.send_task_completed(task)
            except NotificationError:
                # The task is already saved; notifications are best effort.
                pass

        return task

    def delete(self, task_id: int) -> None:
        if not self.repository.delete(task_id):
            raise TaskNotFoundError(f"Task {task_id} not found")

    @staticmethod
    def _validate_payload(
        data: Any,
        *,
        allowed_fields: set[str],
        allow_empty: bool = True,
    ) -> None:
        if not isinstance(data, dict):
            raise ValidationError("JSON body must be an object")
        if not allow_empty and not data:
            raise ValidationError("At least one field is required")

        unknown_fields = set(data) - allowed_fields
        if unknown_fields:
            fields = ", ".join(sorted(unknown_fields))
            raise ValidationError(f"Unknown fields: {fields}")

    @staticmethod
    def _validate_title(value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("title must be a non-empty string")
        return value.strip()

    @staticmethod
    def _validate_completed(value: Any) -> bool:
        if not isinstance(value, bool):
            raise ValidationError("completed must be a boolean")
        return value
