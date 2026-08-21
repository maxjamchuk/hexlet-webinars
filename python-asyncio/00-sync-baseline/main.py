import time


SERVICES = (
    ("auth", 3.0),
    ("billing", 1.0),
    ("notifications", 2.0),
)


def check_service(name: str, delay: float) -> str:
    print(f"Начинаем проверку: {name}")
    time.sleep(delay)
    print(f"Проверка завершена: {name}")
    return f"{name}: OK"


def main() -> None:
    started_at = time.perf_counter()
    results = [check_service(name, delay) for name, delay in SERVICES]
    elapsed = time.perf_counter() - started_at

    print(f"Результаты: {results}")
    print(f"Общее время: {elapsed:.2f} с")


if __name__ == "__main__":
    main()
