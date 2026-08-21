import asyncio
import time


SERVICES = (
    ("fast", 1.0),
    ("medium", 2.0),
    ("slow", 5.0),
)


async def check_service(name: str, delay: float) -> str:
    print(f"Начинаем проверку: {name}")
    try:
        await asyncio.sleep(delay)
    except asyncio.CancelledError:
        print(f"Проверка отменена: {name}")
        raise

    print(f"Проверка завершена: {name}")
    return f"{name}: OK"


async def main() -> None:
    started_at = time.perf_counter()
    try:
        async with asyncio.timeout(2.5):
            async with asyncio.TaskGroup() as group:
                for name, delay in SERVICES:
                    group.create_task(check_service(name, delay))
    except TimeoutError:
        print("Общий таймаут 2.5 с истёк")

    elapsed = time.perf_counter() - started_at
    print(f"Общее время: {elapsed:.2f} с")


if __name__ == "__main__":
    asyncio.run(main())
