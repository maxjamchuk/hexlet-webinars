import json
from pathlib import Path

from app.repository import TaskRepository


def test_get_all_reads_tasks(repository: TaskRepository):
    tasks = repository.get_all()

    assert len(tasks) == 2
    assert tasks[0]["title"] == "Learn pytest"
    assert tasks[1]["completed"] is True


def test_add_saves_task_to_file(
    repository: TaskRepository,
    temporary_data_path: Path,
):
    new_task = {"id": 3, "title": "Learn mocks", "completed": False}

    result = repository.add(new_task)

    assert result == new_task
    assert repository.find_by_id(3) == new_task

    saved_tasks = json.loads(temporary_data_path.read_text(encoding="utf-8"))
    assert saved_tasks[-1] == new_task


def test_update_saves_changes(
    repository: TaskRepository,
    temporary_data_path: Path,
):
    updated = repository.update(1, {"completed": True})

    assert updated["completed"] is True
    assert repository.find_by_id(1)["completed"] is True

    saved_tasks = json.loads(temporary_data_path.read_text(encoding="utf-8"))
    assert saved_tasks[0]["completed"] is True


def test_delete_removes_task_from_file(
    repository: TaskRepository,
    temporary_data_path: Path,
):
    deleted = repository.delete(1)

    assert deleted is True
    assert repository.find_by_id(1) is None

    saved_tasks = json.loads(temporary_data_path.read_text(encoding="utf-8"))
    assert [task["id"] for task in saved_tasks] == [2]
