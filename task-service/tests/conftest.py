import shutil
from pathlib import Path

import pytest

from app import create_app
from app.repository import TaskRepository
from app.service import TaskService


@pytest.fixture
def fixture_path() -> Path:
    return Path(__file__).parent / "fixtures" / "tasks.json"


@pytest.fixture
def temporary_data_path(fixture_path: Path, tmp_path: Path) -> Path:
    data_path = tmp_path / "tasks.json"
    shutil.copyfile(fixture_path, data_path)
    return data_path


@pytest.fixture
def repository(temporary_data_path: Path) -> TaskRepository:
    return TaskRepository(temporary_data_path)


@pytest.fixture
def service(repository: TaskRepository) -> TaskService:
    return TaskService(repository)


@pytest.fixture
def app(temporary_data_path: Path):
    flask_app = create_app(data_path=temporary_data_path)
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()
