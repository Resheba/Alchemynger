# mypy: disable-error-code="attr-defined, comparison-overlap, arg-type"

import pytest

from alchemynger import AsyncManager
from alchemynger.sqlalchemy import select, insert, update, delete

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import ResourceClosedError


@pytest.mark.asyn()
@pytest.mark.usefixtures("setup_db")
@pytest.mark.asyncio()
class TestAsync:
    @staticmethod
    async def test_connect() -> None:
        _manager: AsyncManager = AsyncManager(path="sqlite+aiosqlite:///testA.db")

    @staticmethod
    async def test_session(a_manager: tuple[AsyncManager, type[DeclarativeBase]]) -> None:
        manager, User = a_manager  # noqa: N806
        async with manager.get_session() as session:
            session.add(User(id=1, name="Name"))
            await session.commit()

            assert len((await session.execute(select(User))).scalars().all()) == 1

            await session.execute(delete(User).where(User.id == 1))
            await session.commit()

            assert len((await session.execute(select(User))).scalars().all()) == 0

    @staticmethod
    async def test_execute_insert(a_manager: tuple[AsyncManager, type[DeclarativeBase]]) -> None:
        manager, User = a_manager  # noqa: N806
        data = [(1, "Name1"), (2, "Name2")]
        await manager.execute(statement=insert(User).values(data), commit=True)
        assert len(await manager.execute(select(User))) == len(data)

    @staticmethod
    async def test_execute_scalars(a_manager: tuple[AsyncManager, type[DeclarativeBase]]) -> None:
        manager, User = a_manager  # noqa: N806
        assert await manager.execute(select(User.id, User.name), scalars=False) == [
            (1, "Name1"),
            (2, "Name2"),
        ]

    @staticmethod
    async def test_execute_update(a_manager: tuple[AsyncManager, type[DeclarativeBase]]) -> None:
        manager, User = a_manager  # noqa: N806
        await manager.execute(update(User).where(User.id == 1).values(name="NewName"), commit=True)

        assert await manager.execute(select(User).where(User.name == "NewName"))

    @staticmethod
    async def test_execute_delete(a_manager: tuple[AsyncManager, type[DeclarativeBase]]) -> None:
        manager, User = a_manager  # noqa: N806
        await manager.execute(delete(User).where(User.name == "Name2"), commit=True)

        assert len(await manager.execute(select(User))) == 1

        await manager.execute(delete(User), commit=True)

        assert len(await manager.execute(select(User))) == 0

    @staticmethod
    async def test_raise_close_res(a_manager: tuple[AsyncManager, type[DeclarativeBase]]) -> None:
        manager, User = a_manager  # noqa: N806
        with pytest.raises(ResourceClosedError):
            await manager.execute(insert(User).values(name="Tempo"), ignore_closed_res=False)
