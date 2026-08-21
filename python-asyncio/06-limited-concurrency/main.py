import asyncio
import time

import httpx


BASE_URL = "http://127.0.0.1:8001"
MAX_CONCURRENCY = 3
SERVICE_NAMES = tuple(f"service-{number:02d}" for number in range(1, 11))


async def fetch_status(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    name: str,
) -> str:
    async with semaphore:
        print(f"Начинаем запрос: {name}")
        response = await client.get(
            f"{BASE_URL}/health/{name}",
            params={"delay": 1},
        )
        response.raise_for_status()
        response.json()
        print(f"Завершён запрос: {name}")
    return f"{name}: OK"


async def main() -> int:
    started_at = time.perf_counter()
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            checks = [
                fetch_status(client, semaphore, name)
                for name in SERVICE_NAMES
            ]
            results = await asyncio.gather(*checks)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        print("Не удалось подключиться к локальному серверу.")
        print("Сначала запустите: uv run python mock_server.py")
        return 1

    elapsed = time.perf_counter() - started_at
    print(f"Получено результатов: {len(results)}")
    print(f"Общее время: {elapsed:.2f} с")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
