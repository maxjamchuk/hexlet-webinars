import pytest
import requests

from app.notifications import NotificationClient, NotificationError


def test_send_task_completed_uses_expected_http_request(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            captured["status_checked"] = True

    def fake_post(url, *, json, timeout):
        captured.update(url=url, json=json, timeout=timeout)
        return FakeResponse()

    monkeypatch.setattr("app.notifications.requests.post", fake_post)
    client = NotificationClient("https://notify.example/", timeout=1.5)

    client.send_task_completed(
        {"id": 7, "title": "Learn monkeypatch", "completed": True}
    )

    assert captured == {
        "url": "https://notify.example/notifications",
        "json": {
            "event": "task_completed",
            "task_id": 7,
            "title": "Learn monkeypatch",
        },
        "timeout": 1.5,
        "status_checked": True,
    }


def test_network_error_is_converted_to_notification_error(monkeypatch):
    network_error = requests.RequestException("Network unavailable")

    def raise_network_error(*args, **kwargs):
        raise network_error

    monkeypatch.setattr(
        "app.notifications.requests.post",
        raise_network_error,
    )
    client = NotificationClient("https://notify.example")

    with pytest.raises(NotificationError) as exc:
        client.send_task_completed(
            {"id": 1, "title": "Learn pytest", "completed": True}
        )

    assert exc.value.__cause__ is network_error
