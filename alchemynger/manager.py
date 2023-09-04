from abc import ABC
from contextlib import contextmanager, asynccontextmanager
from typing import Any, AsyncGenerator, Generator, Sequence

from sqlalchemy.exc import ArgumentError, ResourceClosedError
from sqlalchemy import Row, Select, Delete, Update, Insert, TextClause, Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


class Manager(ABC):
    def __init__(self,
                 path: str,
                 auto_connect: bool = False
                 ) -> None:
        self._path: str = path
        
        if auto_connect:
            self.connect()
    
    def connect():
        """
        Connecting with DataBase, create SQLAlchemy `engine`
        """
        ...
    
    def _engine_init():
        ...
    
    def get_session():
        """
        `yield` session with auto `.close()` after `with` statement
        """
        ...
    
    def execute():
        """
        Accept SQLAlchemy statements

        Sync example::

            stmt = insert(User).values(**values)
            manager.execute(stmt, commit=True)

            stmt = select(User)
            result = manager.execute(stmt)
        
        Async example::

            stmt = insert(User).values(**values)
            await manager.execute(stmt, commit=True)

            stmt = select(User)
            result = await manager.execute(stmt)

        """
        ...

    class Base(DeclarativeBase): pass


class SyncManager(Manager):
    """Sync Connection Manger

    E.g.::

        from sqlalchemy import insert
        from alchemynger import SyncManager
        
        manager = SyncManager('sqlite:///path/to/db')

        class User(manager.Base):
            __tablename__ = 'user'
            name = Column(String(30), primary_key=True)

        manager.connect()
        stmt = insert(User).values(name='username')
        manager.execute(stmt, commit=True)

        
    :param path: :class:`str`
     DSN path to DataBase

    :contextmanager get_session:
     `yield` session with auto `.close()` after `with` statement
    
    :method execute
     execute statement and commit if `commit=True`
    """
    
    def connect(self
                ) -> None:
        self._engine_init()

    def _engine_init(self
                     ) -> None:
        try:
            self.engine: Engine = create_engine(self._path)
        except ArgumentError:
            raise ArgumentError(f'Could not parse SQLAlchemy URL from string {self._path}')
        self.Base.metadata.create_all(bind=self.engine)
        self.session_maker: sessionmaker = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self
                    ) -> Generator[Session, None, None]:
        if self.session_maker is None:
            raise Exception(f'The manager is not connected to the database {self._path}')
        with self.session_maker() as session:
            try:
                yield session
            finally:
                session.close()
        
    def execute(self, 
                statement: Select | Delete | Update | Insert | TextClause, 
                commit: bool = False
                ) -> Sequence[Row[Any]] | None :
        with self.get_session() as session:
            result = session.execute(statement=statement)
            try:
                result = result.all()
            except ResourceClosedError:
                result = None

            session.commit() if commit else None
            
            return result


class AsyncManager(Manager):
    """Async Connection Manger

    Simple `INSERT` example::

        from sqlalchemy import insert
        from asyncio import run
        from alchemynger import AsyncManager
        
        manager = AsyncManager('sqlite:///path/to/db')

        class User(manager.Base):
            __tablename__ = 'user'
            name = Column(String(30), primary_key=True)

        async def main():
            await manager.connect()
            stmt = insert(User).values(name='username')
            await manager.execute(stmt, commit=True)
        
        if __name__ == "__main__":
            run(amain())

        
    :param path: :class:`str`
     DSN path to DataBase

    :contextmanager get_session:
     `yield` session with auto `.close()` after `with` statement
    
    :method execute
     execute statement and commit if `commit=True`
    """

    def __init__(self, 
                 path: str
                 ) -> None:
        self._path: str = path
        self.session_maker = None

    async def connect(self
                      ) -> None:
        await self._engine_init()
        
    async def _engine_init(self
                           ) -> None:
        try:
            self.engine: Engine = create_async_engine(self._path)
        except ArgumentError:
            raise ArgumentError(f'Could not parse SQLAlchemy URL from string {self._path}')
        
        async with self.engine.begin() as connect:
            await connect.run_sync(self.Base.metadata.create_all)
        self.session_maker: async_sessionmaker = async_sessionmaker(bind=self.engine)

    @asynccontextmanager
    async def get_session(self
                          ) -> AsyncGenerator[AsyncSession, None]:
        if self.session_maker is None:
            raise Exception(f'The manager is not connected to the database {self._path}')
        async with self.session_maker() as session:
            try:
                yield session
            finally:
                await session.close()
        
    async def execute(self, 
                      statement: Select | Delete | Update | Insert | TextClause, 
                      *, 
                      commit: bool = False
                      ) -> Sequence[Row[Any]] | None :
        async with self.get_session() as session:
            result = await session.execute(statement=statement)
            try:
                result = result.all()
            except ResourceClosedError:
                result = None

            await session.commit() if commit else None

            return result
        