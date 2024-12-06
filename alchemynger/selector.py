from __future__ import annotations

from typing import Any, TYPE_CHECKING

from sqlalchemy import select, delete, update, insert
from sqlalchemy import Select, Delete, Update, Insert, Column

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase


class Selector:
    """
    Technical class for quick generation of sql queries
    """

    def __init__(self, *entities: type[DeclarativeBase] | Column[Any]) -> None:
        self._entities: tuple[type[DeclarativeBase] | Column[Any], ...] = entities

    @property
    def select(self) -> Select[Any]:
        """
        Usage::

            stmt = manager[User].select.where(User.id > 5)
            result = manager.execute(stmt)

        Or Columns::

            stmt = manager[User.id, User.name].select
            result = manager.execute(stmt, scalars=False)

        Also work with AsyncManager::

            result = await manager.execute(stmt)
        """
        return select(*self._entities)

    @property
    def delete(self) -> Delete:
        """
        Usage::

            stmt = manager[User].delete.where(User.id > 5)
            result = manager.execute(stmt, commit=True)

        Also work with AsyncManager::

            result = await manager.execute(stmt, commit=True)
        """
        return delete(*self._entities)

    @property
    def update(self) -> Update:
        """
        Usage::

            stmt = manager[User].update.where(User.name == "Lex").values(name="New")
            result = manager.execute(stmt, commit=True)

        Also work with AsyncManager::

            result = await manager.execute(stmt, commit=True)
        """
        return update(*self._entities)

    @property
    def insert(self) -> Insert:
        """
        Usage::

            stmt = manager[User].insert.values(name="New")
            result = manager.execute(stmt, commit=True)

        Also work with AsyncManager::

            result = await manager.execute(stmt, commit=True)
        """
        return insert(*self._entities)
