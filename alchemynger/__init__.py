"""
## Usage

### SyncManager: Synchronous Database Operations

SyncManager is designed for traditional synchronous applications. Here's how to use it:

```python
from alchemynger import SyncManager
from alchemynger.sqlalchemy import Column, String

# Create a SyncManager instance
manager = SyncManager('sqlite:///path/to/db')

# Define your SQLAlchemy model class
class User(manager.Base):
    __tablename__ = 'user'
    name = Column(String(30), primary_key=True)

# Connect to the database
manager.connect()

# Create an insert statement and execute it
stmt = manager[User].insert.values(name='username')

manager.execute(stmt, commit=True) # or await manager(stmt, commit=True)
```

### AsyncManager: Asynchronous Database Operations

AsyncManager is tailored for asyncio-based applications. Here's how to use it:

```python
from asyncio import run
from alchemynger import AsyncManager
from alchemynger.sqlalchemy import Column, String

# Create an AsyncManager instance
manager = AsyncManager('sqlite+aiosqlite:///path/to/db')

# Define your SQLAlchemy model class
class User(manager.Base):
    __tablename__ = 'user'
    name = Column(String(30), primary_key=True)

# Define an async main function
async def main():
    await manager.connect()
    
    stmt = manager[User].insert.values(name='username')

    await manager.execute(stmt, commit=True) # or await manager(stmt, commit=True)

if __name__ == "__main__":
    run(main())
```

### Selector: Useage

Selectors can be used with Columns, a Column, or the Table Model.

```python
# Create a select statements with column or columns
manager[User.name].select
manager[User.name, User.any_col].select
```

```python
# Create statements with model
manager[User].select
manager[User].delete
manager[User].insert
manager[User].update
```
"""


from .manager import SyncManager, AsyncManager
