import pytest

from alchemynger import SyncManager
from alchemynger.sqlalchemy import select, insert, update, delete


@pytest.mark.usefixtures("setup_db", 'sManager')
class TestSync:
    @staticmethod
    def test_connect():
        manager: SyncManager = SyncManager(path='sqlite:///testS.db')
        manager.connect()

    @staticmethod
    def test_session(sManager: SyncManager and SyncManager):
        manager, User = sManager
        with manager.get_session() as session:
            session.add(User(id=1, name='Name'))
            session.commit()

            assert len(session.execute(select(User)).scalars().all()) == 1
        
            session.query(User).filter(User.id == 1).delete()
            session.commit()
            
            assert len(session.execute(select(User)).scalars().all()) == 0
    
    @staticmethod
    def test_execute_insert(sManager: SyncManager and SyncManager):
        manager, User = sManager
        manager.execute(
            statement=insert(User).values([(1, 'Name1'), (2, 'Name2')]),
            commit=True
        )
        assert len(manager.execute(select(User))) == 2

    @staticmethod
    def test_execute_scalars(sManager: SyncManager and SyncManager):
        manager, User = sManager
        assert manager.execute(select(User.id, User.name), scalars=False) == [(1, 'Name1'), (2, 'Name2')]

    @staticmethod
    def test_execute_update(sManager: SyncManager and SyncManager):
        manager, User = sManager
        manager.execute(update(User).where(User.id == 1).values(name='NewName'), commit=True)

        assert manager.execute(select(User).where(User.name == 'NewName'))

    @staticmethod
    def test_execute_delete(sManager: SyncManager and SyncManager):
        manager, User = sManager
        manager.execute(delete(User).where(User.name == 'Name2'), commit=True)

        assert len(manager.execute(select(User))) == 1

        manager.execute(delete(User), commit=True)
