import asyncio
import time

import httpx


BASE_URL = "http://127.0.0.1:8001"
SERVICES = (
    ("auth", 3.0),
    ("billing", 1.0),
    ("notifications", 2.0),
)


async def fetch_status(
    client: httpx.AsyncClient,
    name: str,
    delay: float,
) -> str:
    print(f"Начинаем HTTP-проверку: {name}")
    response = await client.get(f"{BASE_URL}/health/{name}", params={"delay": delay})
    response.raise_for_status()
    payload: dict[str, object] = response.json()
    print(f"HTTP-проверка завершена: {name}")
    return f"{payload['service']}: OK"


async def main() -> int:
    started_at = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            checks = [fetch_status(client, name, delay) for name, delay in SERVICES]
            results = await asyncio.gather(*checks)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        print("Не удалось подключиться к локальному серверу.")
        print("Сначала запустите: uv run python mock_server.py")
        return 1

    elapsed = time.perf_counter() - started_at
    print(f"Результаты: {results}")
    print(f"Общее время: {elapsed:.2f} с")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
