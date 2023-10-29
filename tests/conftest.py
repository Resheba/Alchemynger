import pytest, sqlite3, pytest_asyncio, asyncio

from alchemynger import SyncManager, AsyncManager
from alchemynger.sqlalchemy import Column, Integer, String


pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    connectA: sqlite3.Connection = sqlite3.connect('testA.db')
    cursorA: sqlite3.Cursor = connectA.cursor()
    cursorA.execute('''DROP TABLE IF EXISTS user;''')
    cursorA.execute('''CREATE TABLE user (
                            id INTEGER NOT NULL, 
                            name VARCHAR(20), 
                            PRIMARY KEY (id)
                        );''')
    connectA.commit()
    
    connectS: sqlite3.Connection = sqlite3.connect('testS.db')
    cursorS: sqlite3.Cursor = connectS.cursor()
    cursorS.execute('''DROP TABLE IF EXISTS user;''')
    cursorS.execute('''CREATE TABLE user (
                            id INTEGER NOT NULL, 
                            name VARCHAR(20), 
                            PRIMARY KEY (id)
                        );''')
    connectS.commit()

    connectA.close(); connectS.close()


@pytest.fixture(scope='session', name='sManager')
def sManager() -> SyncManager:
    manager: SyncManager = SyncManager(path='sqlite:///testS.db')
    
    class User(manager.Base):
        __tablename__ = 'user'

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(30))

        def __repr__(self) -> str:
            return f"User({self.id}, {self.name})"
    
    manager.connect()
    return manager, User


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='function', name='aManager')
async def aManager() -> AsyncManager:
    manager: AsyncManager = AsyncManager(path='sqlite+aiosqlite:///testA.db')
    
    class User(manager.Base):
        __tablename__ = 'user'

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(30))

        def __repr__(self) -> str:
            return f"User({self.id}, {self.name})"
    
    await manager.connect()
    return manager, User
