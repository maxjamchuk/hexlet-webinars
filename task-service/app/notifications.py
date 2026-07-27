from typing import Any

import requests


class NotificationError(Exception):
    pass


class NotificationClient:
    def __init__(self, base_url: str, timeout: float = 2.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def send_task_completed(self, task: dict[str, Any]) -> None:
        try:
            response = requests.post(
                f"{self.base_url}/notifications",
                json={
                    "event": "task_completed",
                    "task_id": task["id"],
                    "title": task["title"],
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise NotificationError("Failed to send notification") from exc
