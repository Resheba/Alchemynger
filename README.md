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
from sqlalchemy import insert
from alchemynger import SyncManager

# Create a SyncManager instance
manager = SyncManager('sqlite:///path/to/db')

# Define your SQLAlchemy model class
class User(manager.Base):
    __tablename__ = 'user'
    name = Column(String(30), primary_key=True)

# Connect to the database
manager.connect()

# Create an insert statement and execute it
stmt = insert(User).values(name='username')
manager.execute(stmt, commit=True)
```

### AsyncManager: Asynchronous Database Operations

AsyncManager is tailored for asyncio-based applications. Here's how to use it:

```python
from sqlalchemy import insert
from asyncio import run
from alchemynger import AsyncManager

# Create an AsyncManager instance
manager = AsyncManager('sqlite:///path/to/db')

# Define your SQLAlchemy model class
class User(manager.Base):
    __tablename__ = 'user'
    name = Column(String(30), primary_key=True)

# Define an async main function
async def main():
    await manager.connect()
    stmt = insert(User).values(name='username')
    await manager.execute(stmt, commit=True)

if __name__ == "__main__":
    run(main())
```

### Context Managers and Error Handling

Both SyncManager and AsyncManager provide context managers for managing database sessions. This ensures that sessions are properly closed, even in the event of an exception.

```python
# Example using a context manager
with manager.get_session() as session:
    stmt = select(User)
    result = manager.execute(stmt)
    # Use the result

# The session is automatically closed when exiting the 'with' block
```

## Contribution

Contributions to Alchemynger are welcome! If you have ideas for improvements, bug fixes, or new features, please open an issue or submit a pull request on the [GitHub repository](https://github.com/Resheba/Alchemynger).

## License

Alchemynger is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
