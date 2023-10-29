import pytest

from alchemynger import SyncManager
from alchemynger.sqlalchemy import select, insert, update, delete


@pytest.mark.usefixtures('sManager')
class TestSelector:
    def test_select(self, sManager: SyncManager and SyncManager):
        manager, User = sManager
        manager: SyncManager

        manager_stmt = manager[User].select
        alchemy_stmt = select(User)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()
        
        manager_stmt = manager[User.id, User.name].select
        alchemy_stmt = select(User.id, User.name)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

    def test_insert(self, sManager: SyncManager and SyncManager):
        manager, User = sManager
        manager: SyncManager

        manager_stmt = manager[User].insert
        alchemy_stmt = insert(User)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

        manager_stmt = manager[User].insert.returning(User.id)
        alchemy_stmt = insert(User).returning(User.id)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

    def test_update(self, sManager: SyncManager and SyncManager):
        manager, User = sManager
        manager: SyncManager

        manager_stmt = manager[User].update
        alchemy_stmt = update(User)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

        manager_stmt = manager[User].update.where(User.id == 1)
        alchemy_stmt = update(User).where(User.id == 1)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

    def test_delete(self, sManager: SyncManager and SyncManager):
        manager, User = sManager
        manager: SyncManager

        manager_stmt = manager[User].delete
        alchemy_stmt = delete(User)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()

        manager_stmt = manager[User].delete.where(User.id == 1)
        alchemy_stmt = delete(User).where(User.id == 1)
        assert manager_stmt.__str__() == alchemy_stmt.__str__()
        