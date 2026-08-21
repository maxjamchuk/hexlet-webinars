import asyncio
import time


class ServiceUnavailableError(RuntimeError):
    pass


async def check_service(
    name: str,
    delay: float,
    should_fail: bool = False,
) -> str:
    print(f"Начинаем проверку: {name}")
    try:
        await asyncio.sleep(delay)
        if should_fail:
            raise ServiceUnavailableError(f"{name} недоступен")
    except asyncio.CancelledError:
        print(f"Проверка отменена: {name}")
        raise

    print(f"Проверка завершена: {name}")
    return f"{name}: OK"


async def main() -> None:
    started_at = time.perf_counter()
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(check_service("auth", 1.0))
            group.create_task(check_service("billing", 2.0, should_fail=True))
            group.create_task(check_service("notifications", 5.0))
    except* ServiceUnavailableError as errors:
        for error in errors.exceptions:
            print(f"Ошибка проверки: {error}")

    elapsed = time.perf_counter() - started_at
    print(f"Общее время: {elapsed:.2f} с")


if __name__ == "__main__":
    asyncio.run(main())
