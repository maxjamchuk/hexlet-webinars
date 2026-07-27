from unittest.mock import Mock

import pytest

from app.notifications import NotificationError
from app.repository import TaskRepository
from app.service import TaskNotFoundError, TaskService, ValidationError


def test_get_all_returns_tasks(service: TaskService):
    tasks = service.get_all()

    assert len(tasks) == 2
    assert tasks[0]["id"] == 1


def test_create_task_with_valid_data(service: TaskService):
    task = service.create({"title": "Learn mocks"})

    assert task == {
        "id": 3,
        "title": "Learn mocks",
        "completed": False,
    }
    assert service.get_by_id(3) == task


def test_update_task_title(service: TaskService):
    task = service.update(1, {"title": "Learn fixtures"})

    assert task["title"] == "Learn fixtures"
    assert task["completed"] is False


def test_update_task_completed(service: TaskService):
    task = service.update(1, {"completed": True})

    assert task["completed"] is True
    assert service.get_by_id(1)["completed"] is True


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "   "},
        {"title": "Invalid completed", "completed": "yes"},
        {"title": "Unknown field", "priority": "high"},
    ],
    ids=[
        "missing title",
        "empty title",
        "invalid completed",
        "unknown field",
    ],
)
def test_create_task_rejects_invalid_data(service: TaskService, payload):
    with pytest.raises(ValidationError):
        service.create(payload)


def test_update_rejects_empty_payload(service: TaskService):
    with pytest.raises(ValidationError):
        service.update(1, {})


def test_get_missing_task_raises_error(service: TaskService):
    with pytest.raises(TaskNotFoundError):
        service.get_by_id(999)


def test_update_completed_sends_notification(repository: TaskRepository):
    notification_client = Mock()
    service = TaskService(repository, notification_client)

    task = service.update(1, {"completed": True})

    notification_client.send_task_completed.assert_called_once_with(task)


def test_repeated_completed_update_does_not_send_notification(
    repository: TaskRepository,
):
    notification_client = Mock()
    service = TaskService(repository, notification_client)

    service.update(2, {"completed": True})

    notification_client.send_task_completed.assert_not_called()


def test_title_update_does_not_send_notification(repository: TaskRepository):
    notification_client = Mock()
    service = TaskService(repository, notification_client)

    service.update(1, {"title": "Learn Mock"})

    notification_client.send_task_completed.assert_not_called()


def test_notification_error_does_not_cancel_update(repository: TaskRepository):
    notification_client = Mock()
    notification_client.send_task_completed.side_effect = NotificationError(
        "Service unavailable"
    )
    service = TaskService(repository, notification_client)

    task = service.update(1, {"completed": True})

    assert task["completed"] is True
    assert repository.find_by_id(1)["completed"] is True
    notification_client.send_task_completed.assert_called_once_with(task)
