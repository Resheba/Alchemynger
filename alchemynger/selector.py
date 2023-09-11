from sqlalchemy import Sequence, select, delete, update, insert
from sqlalchemy import Select, Delete, Update, Insert, Column
from sqlalchemy.orm import DeclarativeBase


class Selector:
    """
    Technical class for quick generation of sql queries
    """
    def __init__(
            self,
            *entities: Sequence[DeclarativeBase | Column]
            ) -> None:
        self._entities: Sequence[DeclarativeBase | Column] = entities
    
    @property
    def select(
        self
        ) -> Select:
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
    def delete(
            self
               ) -> Delete:
        """
        Usage::

            stmt = manager[User].delete.where(User.id > 5)
            result = manager.execute(stmt, commit=True)

        Also work with AsyncManager::

            result = await manager.execute(stmt, commit=True)
        """
        return delete(*self._entities)
    
    @property
    def update(
            self
            ) -> Update:
        """
        Usage::

            stmt = manager[User].update.where(User.name == "Lex").values(name="New")
            result = manager.execute(stmt, commit=True)

        Also work with AsyncManager::

            result = await manager.execute(stmt, commit=True)
        """
        return update(*self._entities)
    
    @property
    def insert(
            self
               ) -> Insert:
        """
        Usage::

            stmt = manager[User].insert.values(name="New")
            result = manager.execute(stmt, commit=True)

        Also work with AsyncManager::

            result = await manager.execute(stmt, commit=True)
        """
        return insert(*self._entities)
    