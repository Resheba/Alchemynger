# Alchemynger: SQLAlchemy Connection Manager

Alchemynger is a versatile Python library that simplifies database connectivity and interaction using SQLAlchemy. It offers both synchronous and asynchronous database management for applications that require efficient database operations. 


## Installation

You can install Alchemynger using pip:

```bash
pip install alchemynger
```

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

## Native use of SQLAlchemy queries
You can also utilize the standard query-writing methods provided by SQLAlchemy, for example, if you find that the library's functionality is insufficient for your needs. Just user `from sqlalchemy import select, insert, ...` or import from `from alchemynger import select, insert`

```python
from alchemynger import SyncManager
from alchemynger.sqlalchemy import select, insert, Column

# Create a SyncManager instance
manager = SyncManager('sqlite:///path/to/db')

# Define your SQLAlchemy model class
class User(manager.Base):
    __tablename__ = 'user'
    name = Column(String(30), primary_key=True)

# Connect to the database
manager.connect()

# Create a select statement and execute it

stmt = select(User).where(User.id > 5)

manager.execute(stmt)

# Create an insert statement and execute it
stmt = insert(User).values(name="Lex")

manager.execute(stmt, commit=True) # or await manager(stmt, commit=True)
```

### Context Managers and Error Handling

Both SyncManager and AsyncManager provide context managers for managing database sessions. This ensures that sessions are properly closed, even in the event of an exception.

```python
# Example using a context manager
with manager.get_session() as session:
    stmt = manager[User].select

    result = session.execute(stmt)
    # Use the result
```

## Contribution

Contributions to Alchemynger are welcome! If you have ideas for improvements, bug fixes, or new features, please open an issue or submit a pull request on the [GitHub repository](https://github.com/Resheba/Alchemynger).

## License

Alchemynger is licensed under the MIT License. See the [LICENSE](https://github.com/Resheba/Alchemynger/blob/main/LICENSE) file for more details.
