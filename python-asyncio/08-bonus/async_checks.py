import asyncio
from collections.abc import Awaitable, Callable, Sequence


async def collect_statuses(
    names: Sequence[str],
    checker: Callable[[str], Awaitable[str]],
) -> list[str]:
    checks = [checker(name) for name in names]
    return list(await asyncio.gather(*checks))
