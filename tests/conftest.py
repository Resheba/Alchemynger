import pytest
import sqlite3
import pytest_asyncio

from alchemynger import SyncManager, AsyncManager
from alchemynger.sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(name="setup_db", scope="session", autouse=True)
def _setup_db() -> None:
    connect_a: sqlite3.Connection = sqlite3.connect("testA.db")
    cursor_a: sqlite3.Cursor = connect_a.cursor()
    cursor_a.execute("""DROP TABLE IF EXISTS user;""")
    cursor_a.execute("""CREATE TABLE user (
                            id INTEGER NOT NULL,
                            name VARCHAR(20),
                            PRIMARY KEY (id)
                        );""")
    connect_a.commit()

    connect_s: sqlite3.Connection = sqlite3.connect("testS.db")
    cursor_s: sqlite3.Cursor = connect_s.cursor()
    cursor_s.execute("""DROP TABLE IF EXISTS user;""")
    cursor_s.execute("""CREATE TABLE user (
                            id INTEGER NOT NULL,
                            name VARCHAR(20),
                            PRIMARY KEY (id)
                        );""")
    connect_s.commit()

    connect_a.close()
    connect_s.close()


@pytest.fixture(scope="session", name="s_manager")
def s_manager() -> tuple[SyncManager, type[DeclarativeBase]]:
    manager: SyncManager = SyncManager(path="sqlite:///testS.db")

    class User(manager.Base):  # type: ignore[name-defined]
        __tablename__ = "user"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(30))

        def __repr__(self) -> str:
            return f"User({self.id}, {self.name})"

    manager.create_all()
    return manager, User


@pytest_asyncio.fixture(scope="function", name="a_manager")
async def a_manager() -> tuple[AsyncManager, type[DeclarativeBase]]:
    manager: AsyncManager = AsyncManager(path="sqlite+aiosqlite:///testA.db")

    class User(manager.Base):  # type: ignore[name-defined]
        __tablename__ = "user"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(30))

        def __repr__(self) -> str:
            return f"User({self.id}, {self.name})"

    await manager.create_all()
    return manager, User
