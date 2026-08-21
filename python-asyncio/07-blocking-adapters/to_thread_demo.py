import asyncio
import time


def timestamp(started_at: float) -> str:
    return f"{time.perf_counter() - started_at:.1f} с"


def load_report() -> str:
    time.sleep(2.0)
    return "Отчёт загружен"


async def heartbeat(started_at: float) -> None:
    for _ in range(5):
        await asyncio.sleep(0.5)
        print(f"[{timestamp(started_at)}] heartbeat")


async def load_report_in_thread(started_at: float) -> None:
    print(f"[{timestamp(started_at)}] Передаём блокирующий I/O в поток")
    result = await asyncio.to_thread(load_report)
    print(f"[{timestamp(started_at)}] {result}")


async def main() -> None:
    started_at = time.perf_counter()
    await asyncio.gather(
        heartbeat(started_at),
        load_report_in_thread(started_at),
    )


if __name__ == "__main__":
    asyncio.run(main())
