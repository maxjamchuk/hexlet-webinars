import asyncio
import time


def timestamp(started_at: float) -> str:
    return f"{time.perf_counter() - started_at:.1f} с"


async def heartbeat(started_at: float) -> None:
    for _ in range(5):
        await asyncio.sleep(0.5)
        print(f"[{timestamp(started_at)}] heartbeat")


async def load_report(started_at: float) -> None:
    print(f"[{timestamp(started_at)}] Начинаем блокирующий вызов")
    time.sleep(2.0)
    print(f"[{timestamp(started_at)}] Блокирующий вызов завершён")


async def main() -> None:
    started_at = time.perf_counter()
    await asyncio.gather(
        heartbeat(started_at),
        load_report(started_at),
    )


if __name__ == "__main__":
    asyncio.run(main())
