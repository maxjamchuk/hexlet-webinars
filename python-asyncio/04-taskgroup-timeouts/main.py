import asyncio
import time


SERVICES = (
    ("auth", 1.5),
    ("billing", 0.5),
    ("notifications", 1.0),
)


async def check_service(name: str, delay: float) -> str:
    print(f"Начинаем проверку: {name}")
    await asyncio.sleep(delay)
    print(f"Проверка завершена: {name}")
    return f"{name}: OK"


async def main() -> None:
    started_at = time.perf_counter()
    tasks: list[asyncio.Task[str]] = []

    async with asyncio.TaskGroup() as group:
        for name, delay in SERVICES:
            tasks.append(group.create_task(check_service(name, delay)))

    results = [task.result() for task in tasks]
    elapsed = time.perf_counter() - started_at
    print(f"Результаты: {results}")
    print(f"Общее время: {elapsed:.2f} с")


if __name__ == "__main__":
    asyncio.run(main())
