from __future__ import annotations

from abc import abstractmethod
from abc import ABC
from contextlib import contextmanager
from contextlib import asynccontextmanager
from typing import Any
from typing import overload
from typing import TYPE_CHECKING
from collections.abc import AsyncGenerator
from collections.abc import Generator
from collections.abc import Sequence

from sqlalchemy.exc import ArgumentError
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import Row
from sqlalchemy import Select
from sqlalchemy import Delete
from sqlalchemy import Update
from sqlalchemy import Insert
from sqlalchemy import TextClause
from sqlalchemy import Engine
from sqlalchemy import MetaData
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

if TYPE_CHECKING:
    from sqlalchemy.engine import URL


class Manager(ABC):
    Base: DeclarativeBase
    _session_maker_type: type
    _engine_fabric: Any
    session_maker: Any = None
    _session_type: type

    @overload
    def __init__(
        self,
        path: str | URL,
        *,
        metadata: MetaData | None = ...,
        autoflush: bool = ...,
        expire_on_commit: bool = ...,
        session_type: type = ...,
        **session_maker_kwargs: Any,
    ) -> None: ...

    @overload
    def __init__(
        self,
        path: str | URL,
        *,
        base: DeclarativeBase | None = ...,
        autoflush: bool = ...,
        expire_on_commit: bool = ...,
        session_type: type = ...,
        **session_maker_kwargs: Any,
    ) -> None: ...

    def __init__(
        self,
        path: str | URL,
        *,
        metadata: MetaData | None = None,
        base: DeclarativeBase | None = None,
        autoflush: bool = True,
        expire_on_commit: bool = True,
        session_type: type | None = None,
        **session_maker_kwargs: Any,
    ) -> None:
        self._path: URL | str = path
        if base is not None:
            self.Base = base
        else:
            self.Base: DeclarativeBase = declarative_base(metadata=metadata)
        self._engine_init(
            session_type=session_type,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
            **session_maker_kwargs,
        )

    def _engine_init(
        self,
        *,
        session_type: type | None,
        autoflush: bool,
        expire_on_commit: bool,
        **kwargs: Any,
    ) -> None:
        try:
            self.engine = self.__class__._engine_fabric(self._path)  # noqa: SLF001
        except ArgumentError as ex:
            raise BadPathError(f"Could not parse SQLAlchemy URL from string {self._path}") from ex
        if session_type is not None:
            kwargs.setdefault("class_", session_type)
        self.session_maker = self.__class__._session_maker_type(  # noqa: SLF001
            bind=self.engine,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
            **kwargs,
        )

    def __getitem__(
        self,
        entities: type[DeclarativeBase] | Column[Any] | tuple[Any, ...],
    ) -> Selector:
        if isinstance(entities, Sequence):
            return Selector(*entities)
        return Selector(entities)

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

    engine: Engine
    _session_maker_type: type[sessionmaker[Any]] = sessionmaker
    _engine_fabric = create_engine
    _session_type: type[Session] = Session
    session_maker: sessionmaker[Any] | None

    def create_all(
        self,
        tables: Sequence[Table] | None = None,
        *,
        checkfirst: bool = True,
    ) -> None:
        self.Base.metadata.create_all(bind=self.engine, tables=tables, checkfirst=checkfirst)

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

    engine: AsyncEngine
    _session_maker_type: type[async_sessionmaker[Any]] = async_sessionmaker
    _engine_fabric = create_async_engine
    _session_type: type[AsyncSession] = AsyncSession
    session_maker: async_sessionmaker[Any] | None

    async def create_all(
        self,
        tables: Sequence[Table] | None = None,
        *,
        checkfirst: bool = True,
    ) -> None:
        async with self.engine.begin() as connect:
            await connect.run_sync(
                self.Base.metadata.create_all,
                tables=tables,
                checkfirst=checkfirst,
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
