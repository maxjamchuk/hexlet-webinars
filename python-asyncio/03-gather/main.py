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
    checks = [check_service(name, delay) for name, delay in SERVICES]
    results = await asyncio.gather(*checks)
    elapsed = time.perf_counter() - started_at

    print(f"Результаты gather: {results}")
    print(f"Общее время: {elapsed:.2f} с")


if __name__ == "__main__":
    asyncio.run(main())
