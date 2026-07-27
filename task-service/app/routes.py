from flask import Blueprint, current_app, jsonify, request

from .service import TaskNotFoundError, TaskService, ValidationError

tasks_blueprint = Blueprint("tasks", __name__)


def get_task_service() -> TaskService:
    return current_app.extensions["task_service"]


@tasks_blueprint.get("/tasks")
def list_tasks():
    return jsonify(get_task_service().get_all())


@tasks_blueprint.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    try:
        task = get_task_service().get_by_id(task_id)
    except TaskNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    return jsonify(task)


@tasks_blueprint.post("/tasks")
def create_task():
    payload = request.get_json(silent=True)

    try:
        task = get_task_service().create(payload)
    except ValidationError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(task), 201


@tasks_blueprint.patch("/tasks/<int:task_id>")
def update_task(task_id: int):
    payload = request.get_json(silent=True)

    try:
        task = get_task_service().update(task_id, payload)
    except ValidationError as error:
        return jsonify({"error": str(error)}), 400
    except TaskNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    return jsonify(task)


@tasks_blueprint.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    try:
        get_task_service().delete(task_id)
    except TaskNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    return "", 204
