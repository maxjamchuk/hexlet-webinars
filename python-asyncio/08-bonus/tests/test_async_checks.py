from unittest.mock import AsyncMock

import pytest

from async_checks import collect_statuses


@pytest.mark.asyncio
async def test_collect_statuses_preserves_order() -> None:
    names = ["auth", "billing", "notifications"]
    checker = AsyncMock(side_effect=lambda name: f"{name}: OK")

    result = await collect_statuses(names, checker)

    assert result == ["auth: OK", "billing: OK", "notifications: OK"]
    assert checker.await_count == 3
    assert [call.args[0] for call in checker.await_args_list] == names


@pytest.mark.asyncio
async def test_collect_statuses_propagates_checker_error() -> None:
    checker = AsyncMock(
        side_effect=["auth: OK", RuntimeError("billing is unavailable")],
    )

    with pytest.raises(RuntimeError, match="billing is unavailable"):
        await collect_statuses(["auth", "billing"], checker)

    assert checker.await_count == 2
