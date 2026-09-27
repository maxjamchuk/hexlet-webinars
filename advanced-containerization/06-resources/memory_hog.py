"""Запускать в контейнере с --memory=64m --memory-swap=64m."""

import time

blocks = []
while True:
    blocks.append(b"x" * (4 * 1024 * 1024))
    print(f"allocated: {len(blocks) * 4} MiB", flush=True)
    time.sleep(1)
