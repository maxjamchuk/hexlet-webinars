import asyncio

import httpx


BASE_URL = "http://127.0.0.1:8001"
SERVICES = (
    ("auth", 1.0, 200),
    ("billing", 1.0, 503),
    ("reports", 4.0, 200),
)


async def fetch_status(
    client: httpx.AsyncClient,
    name: str,
    delay: float,
    status_code: int,
) -> str:
    try:
        response = await client.get(
            f"{BASE_URL}/health/{name}",
            params={"delay": delay, "status": status_code},
        )
        response.raise_for_status()
        response.json()
        return f"{name}: OK"
    except httpx.ConnectTimeout:
        raise
    except httpx.HTTPStatusError as error:
        return f"{name}: HTTP {error.response.status_code}"
    except httpx.TimeoutException:
        return f"{name}: timeout"


async def main() -> int:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            checks = [fetch_status(client, *service) for service in SERVICES]
            results = await asyncio.gather(*checks)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        print("Не удалось подключиться к локальному серверу.")
        print("Сначала запустите: uv run python mock_server.py")
        return 1

    print("Результаты проверок:")
    for result in results:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
