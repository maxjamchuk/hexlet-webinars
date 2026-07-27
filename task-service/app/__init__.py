from pathlib import Path

from flask import Flask

from .notifications import NotificationClient
from .repository import TaskRepository
from .routes import tasks_blueprint
from .service import TaskService


def create_app(
    data_path: str | Path | None = None,
    repository: TaskRepository | None = None,
    service: TaskService | None = None,
    notification_client: NotificationClient | None = None,
) -> Flask:
    app = Flask(__name__)

    if service is None:
        if repository is None:
            default_path = Path(__file__).resolve().parent.parent / "data" / "tasks.json"
            repository = TaskRepository(data_path or default_path)
        service = TaskService(repository, notification_client)

    app.extensions["task_service"] = service
    app.register_blueprint(tasks_blueprint)

    return app
