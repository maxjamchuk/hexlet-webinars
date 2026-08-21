import asyncio


WORKER_COUNT = 2
JOB_COUNT = 6


async def producer(queue: asyncio.Queue[int | None]) -> None:
    for job_number in range(1, JOB_COUNT + 1):
        await queue.put(job_number)
        print(f"Producer добавил задание {job_number}")

    for _ in range(WORKER_COUNT):
        await queue.put(None)


async def worker(name: str, queue: asyncio.Queue[int | None]) -> None:
    while True:
        job_number = await queue.get()
        try:
            if job_number is None:
                print(f"{name} завершает работу")
                return

            print(f"{name} обрабатывает задание {job_number}")
            await asyncio.sleep(0.3)
            print(f"{name} завершил задание {job_number}")
        finally:
            queue.task_done()


async def main() -> None:
    queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=2)
    producer_task = asyncio.create_task(producer(queue))
    worker_tasks = [
        asyncio.create_task(worker(f"worker-{number}", queue))
        for number in range(1, WORKER_COUNT + 1)
    ]

    await producer_task
    await queue.join()
    await asyncio.gather(*worker_tasks)
    print("Все задания обработаны")


if __name__ == "__main__":
    asyncio.run(main())
