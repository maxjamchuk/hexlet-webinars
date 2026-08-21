import asyncio
import time


SERVICES = (
    ("auth", 3.0),
    ("billing", 1.0),
    ("notifications", 2.0),
)


async def check_service(name: str, delay: float) -> str:
    print(f"Начинаем проверку: {name}")
    await asyncio.sleep(delay)
    print(f"Проверка завершена: {name}")
    return f"{name}: OK"


async def main() -> None:
    started_at = time.perf_counter()
    results: list[str] = []

    for name, delay in SERVICES:
        result = await check_service(name, delay)
        results.append(result)

    elapsed = time.perf_counter() - started_at
    print(f"Результаты: {results}")
    print(f"Общее время: {elapsed:.2f} с")


if __name__ == "__main__":
    asyncio.run(main())
