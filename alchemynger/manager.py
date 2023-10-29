from contextlib import contextmanager, asynccontextmanager
from typing import Any, AsyncGenerator, Generator, Iterable, Sequence

from sqlalchemy.exc import ArgumentError, ResourceClosedError
from sqlalchemy import Column, Row, Select, Delete, Update, Insert, TextClause, Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

from .selector import Selector


class Manager:
    def __init__(
                 self,
                 path: str,
                 auto_connect: bool = False
                ) -> None:
        self._path: str = path
        self.Base: DeclarativeMeta = declarative_base()
        
        if auto_connect:
            self.connect()
    
    def __getitem__(
            self, 
            entities: Sequence[DeclarativeBase | Column]):
        if issubclass(type(entities), Iterable):
            return Selector(*entities)
        return Selector(entities)

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

    # class Base(DeclarativeBase): pass


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
    
    def connect(
                 self
                ) -> None:
        self._engine_init()

    def _engine_init(
                     self
                    ) -> None:
        try:
            self.engine: Engine = create_engine(self._path)
        except ArgumentError:
            raise ArgumentError(f'Could not parse SQLAlchemy URL from string {self._path}')
        self.Base.metadata.create_all(bind=self.engine)
        self.session_maker: sessionmaker = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(
                     self
                    ) -> Generator[Session, None, None]:
        if self.session_maker is None:
            raise Exception(f'The manager is not connected to the database {self._path}')
        with self.session_maker() as session:
            try:
                yield session
            finally:
                session.close()
 
    @property
    def session(self) -> Session:
        """
        Property that provides a SQLAlchemy session for database operations.

        Usage::

            result = manager.session.query(User).all()
        """
        with self.get_session() as session:
            return session
        
    def execute(
                 self, 
                 statement: Select | Delete | Update | Insert | TextClause, 
                 commit: bool = False,
                 scalars: bool = True
                ) -> Sequence[Row[Any]] | None :
        with self.get_session() as session:
            result = session.execute(statement=statement)
            try:
                result = result.scalars().all() if scalars else result.all()
            except ResourceClosedError:
                result = None

            session.commit() if commit else None
            
            return result
    
    def __call__(self, 
                     statement: Select | Delete | Update | Insert | TextClause, 
                     *, 
                     commit: bool = False,
                     scalars: bool = True
                    ) -> Sequence[Row[Any]] | None:
        return self.execute(
            statement=statement,
            commit=commit,
            scalars=scalars
        )     


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

    def __init__(
                 self, 
                 path: str
                ) -> None:
        self._path: str = path
        self.session_maker = None

        self.Base: DeclarativeMeta = declarative_base()

    async def connect(
                     self
                    ) -> None:
        await self._engine_init()
        
    async def _engine_init(
                         self
                        ) -> None:
        try:
            self.engine: Engine = create_async_engine(self._path)
        except ArgumentError:
            raise ArgumentError(f'Could not parse SQLAlchemy URL from string {self._path}')
        
        async with self.engine.begin() as connect:
            await connect.run_sync(self.Base.metadata.create_all)
        self.session_maker: async_sessionmaker = async_sessionmaker(bind=self.engine)

    @asynccontextmanager
    async def get_session(
                         self
                        ) -> AsyncGenerator[AsyncSession, None]:
        if self.session_maker is None:
            raise Exception(f'The manager is not connected to the database {self._path}')
        async with self.session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    @property
    async def session(self) -> AsyncSession:
        """
        Property that provides a SQLAlchemy session for database operations.

        Usage::

            session = await manager.session
            session.add(User(name='name'))
            await session.commit()
        """
        async with self.get_session() as session:
            return session

    async def execute(
                     self, 
                     statement: Select | Delete | Update | Insert | TextClause, 
                     *, 
                     commit: bool = False,
                     scalars: bool = True
                    ) -> Sequence[Row[Any]] | None:
        async with self.get_session() as session:
            result = await session.execute(statement=statement)
            try:
                result = result.scalars().all() if scalars else result.all()
            except ResourceClosedError:
                result = None

            await session.commit() if commit else None

            return result
    
    async def __call__(self, 
                     statement: Select | Delete | Update | Insert | TextClause, 
                     *, 
                     commit: bool = False,
                     scalars: bool = True
                    ) -> Sequence[Row[Any]] | None:
        return await self.execute(
            statement=statement,
            commit=commit,
            scalars=scalars
        )
        