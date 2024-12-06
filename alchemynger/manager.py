from __future__ import annotations

from abc import abstractmethod
from abc import ABC
from contextlib import contextmanager
from contextlib import asynccontextmanager
from typing import Any
from collections.abc import AsyncGenerator
from collections.abc import Generator
from collections.abc import Sequence

from sqlalchemy.exc import ArgumentError
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy import Column
from sqlalchemy import Row
from sqlalchemy import Select
from sqlalchemy import Delete
from sqlalchemy import Update
from sqlalchemy import Insert
from sqlalchemy import TextClause
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from .selector import Selector
from .exception import BadPathError


class Manager(ABC):
    Base: DeclarativeBase

    def __getitem__(
        self,
        entities: type[DeclarativeBase] | Column[Any] | tuple[Any, ...],
    ) -> Selector:
        if isinstance(entities, Sequence):
            return Selector(*entities)
        return Selector(entities)

    @abstractmethod
    def connect(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """
        Connecting with DataBase, create SQLAlchemy `engine`
        """

    @abstractmethod
    def _engine_init(self, *args: Any, **kwargs: Any) -> Any: ...  # noqa: ANN401

    @abstractmethod
    def get_session(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """
        yield session with auto `.close()` after `with` statement
        """

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
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

    def __init__(self, path: str) -> None:
        self._path: str = path
        self.Base: DeclarativeBase = declarative_base()
        self.session_maker: sessionmaker[Any] | None = None

    def connect(self, *, create_all: bool = True) -> None:
        self._engine_init(create_all=create_all)

    def _engine_init(self, *, create_all: bool) -> None:
        try:
            self.engine: Engine = create_engine(self._path)
        except ArgumentError as ex:
            raise BadPathError(f"Could not parse SQLAlchemy URL from string {self._path}") from ex
        if create_all:
            self.Base.metadata.create_all(bind=self.engine)
        self.session_maker = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        if self.session_maker is None:
            raise RuntimeError(
                f"The manager is is missing engine or/and session maker {self._path}",
            )
        with self.session_maker() as session:
            try:
                yield session
            finally:
                session.close()

    def execute(
        self,
        statement: Select[Any] | Delete | Update | Insert | TextClause,
        *,
        commit: bool = False,
        scalars: bool = True,
    ) -> Sequence[Row[Any]] | None:
        with self.get_session() as session:
            result = session.execute(statement=statement)
            try:
                scal_or_rows = result.scalars().all() if scalars else result.all()
            except ResourceClosedError:
                scal_or_rows = None

            session.commit() if commit else None

            return scal_or_rows

    def __call__(
        self,
        statement: Select[Any] | Delete | Update | Insert | TextClause,
        *,
        commit: bool = False,
        scalars: bool = True,
    ) -> Sequence[Row[Any]] | None:
        return self.execute(statement=statement, commit=commit, scalars=scalars)


class AsyncManager(Manager):
    """Async Connection Manger

    Simple `INSERT` example::

        from sqlalchemy import insert
        from asyncio import run
        from alchemynger import AsyncManager

        manager = AsyncManager('sqlite+aiosqlite:///path/to/db')

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

    def __init__(self, path: str) -> None:
        self._path: str = path
        self.session_maker: async_sessionmaker[Any] | None = None

        self.Base: DeclarativeBase = declarative_base()

    async def connect(
        self,
        *,
        create_all: bool = True,
        autoflush: bool = True,
        expire_on_commit: bool = True,
    ) -> None:
        await self._engine_init(
            create_all=create_all,
            expire_on_commit=expire_on_commit,
            autoflush=autoflush,
        )

    async def _engine_init(
        self,
        *,
        create_all: bool,
        autoflush: bool = True,
        expire_on_commit: bool = True,
    ) -> None:
        try:
            self.engine: AsyncEngine = create_async_engine(self._path)
        except ArgumentError as ex:
            raise BadPathError(f"Could not parse SQLAlchemy URL from string {self._path}") from ex
        if create_all:
            async with self.engine.begin() as connect:
                await connect.run_sync(self.Base.metadata.create_all)
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=expire_on_commit,
            autoflush=autoflush,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self.session_maker is None:
            raise RuntimeError(
                f"The manager is is missing engine or/and session maker {self._path}",
            )
        async with self.session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    async def execute(
        self,
        statement: Select[Any] | Delete | Update | Insert | TextClause,
        *,
        commit: bool = False,
        scalars: bool = True,
    ) -> Sequence[Row[Any]] | None:
        async with self.get_session() as session:
            result = await session.execute(statement=statement)
            try:
                scal_or_rows = result.scalars().all() if scalars else result.all()
            except ResourceClosedError:
                scal_or_rows = None

            await session.commit() if commit else None

            return scal_or_rows

    async def __call__(
        self,
        statement: Select[Any] | Delete | Update | Insert | TextClause,
        *,
        commit: bool = False,
        scalars: bool = True,
    ) -> Sequence[Row[Any]] | None:
        return await self.execute(statement=statement, commit=commit, scalars=scalars)
