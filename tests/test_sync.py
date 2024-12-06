# mypy: disable-error-code="attr-defined, comparison-overlap, arg-type"

import pytest

from alchemynger import SyncManager
from alchemynger.sqlalchemy import select, insert, update, delete

from sqlalchemy.orm import DeclarativeBase


@pytest.mark.usefixtures("setup_db", "s_manager")
class TestSync:
    @staticmethod
    def test_connect() -> None:
        _manager: SyncManager = SyncManager(path="sqlite:///testS.db")

    @staticmethod
    def test_session(s_manager: tuple[SyncManager, type[DeclarativeBase]]) -> None:
        manager, User = s_manager  # noqa: N806
        with manager.get_session() as session:
            session.add(User(id=1, name="Name"))
            session.commit()

            assert len(session.execute(select(User)).scalars().all()) == 1

            session.query(User).filter(User.id == 1).delete()
            session.commit()

            assert len(session.execute(select(User)).scalars().all()) == 0

    @staticmethod
    def test_execute_insert(s_manager: tuple[SyncManager, type[DeclarativeBase]]) -> None:
        manager, User = s_manager  # noqa: N806
        data = [(1, "Name1"), (2, "Name2")]
        manager.execute(statement=insert(User).values(data), commit=True)
        assert len(manager.execute(select(User))) == len(data)

    @staticmethod
    def test_execute_scalars(s_manager: tuple[SyncManager, type[DeclarativeBase]]) -> None:
        manager, User = s_manager  # noqa: N806
        assert manager.execute(select(User.id, User.name), scalars=False) == [
            (1, "Name1"),
            (2, "Name2"),
        ]

    @staticmethod
    def test_execute_update(s_manager: tuple[SyncManager, type[DeclarativeBase]]) -> None:
        manager, User = s_manager  # noqa: N806
        manager.execute(update(User).where(User.id == 1).values(name="NewName"), commit=True)

        assert manager.execute(select(User).where(User.name == "NewName"))

    @staticmethod
    def test_execute_delete(s_manager: tuple[SyncManager, type[DeclarativeBase]]) -> None:
        manager, User = s_manager  # noqa: N806
        manager.execute(delete(User).where(User.name == "Name2"), commit=True)

        assert len(manager.execute(select(User))) == 1

        manager.execute(delete(User), commit=True)
