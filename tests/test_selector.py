# mypy: disable-error-code="attr-defined, comparison-overlap, arg-type"

import pytest

from alchemynger import SyncManager
from alchemynger.sqlalchemy import select, insert, update, delete

from sqlalchemy.orm import DeclarativeBase


@pytest.mark.usefixtures("s_manager")
class TestSelector:
    def test_select(self, s_manager: tuple[SyncManager, type[DeclarativeBase]]) -> None:
        manager, User = s_manager  # noqa: N806

        manager_stmt = manager[User].select
        alchemy_stmt1 = select(User)
        assert manager_stmt.__str__() == alchemy_stmt1.__str__()

        manager_stmt = manager[User.id, User.name].select
        alchemy_stmt = select(User.id, User.name)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

    def test_insert(self, s_manager: tuple[SyncManager, type[DeclarativeBase]]) -> None:
        manager, User = s_manager  # noqa: N806

        manager_stmt = manager[User].insert
        alchemy_stmt = insert(User)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

        manager_stmt = manager[User].insert.returning(User.id)
        alchemy_stmt = insert(User).returning(User.id)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

    def test_update(self, s_manager: tuple[SyncManager, type[DeclarativeBase]]) -> None:
        manager, User = s_manager  # noqa: N806

        manager_stmt = manager[User].update
        alchemy_stmt = update(User)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

        manager_stmt = manager[User].update.where(User.id == 1)
        alchemy_stmt = update(User).where(User.id == 1)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

    def test_delete(self, s_manager: tuple[SyncManager, type[DeclarativeBase]]) -> None:
        manager, User = s_manager  # noqa: N806

        manager_stmt = manager[User].delete
        alchemy_stmt = delete(User)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

        manager_stmt = manager[User].delete.where(User.id == 1)
        alchemy_stmt = delete(User).where(User.id == 1)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()
