import asyncio


async def check_service(name: str, delay: float) -> str:
    print(f"Начинаем проверку: {name}")
    await asyncio.sleep(delay)
    print(f"Проверка завершена: {name}")
    return f"{name}: OK"


async def main() -> None:
    coroutine = check_service("auth", 1.0)
    print(f"Создан объект: {type(coroutine).__name__}")

    result = await coroutine
    print(f"Результат: {result}")


if __name__ == "__main__":
    asyncio.run(main())
