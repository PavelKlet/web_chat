from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import async_sessionmaker

class IUnitOfWork(ABC):
    """
        An abstract base class that defines the contract for the Unit of Work pattern.
        The Unit of Work handles transactions, allowing commit or rollback operations on
        all changes made within a session.
    """

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...

    @abstractmethod
    def set_repository(self, name, repository_class): ...

    @abstractmethod
    def __getattr__(self, name): ...


class UnitOfWork(IUnitOfWork):
    """
        Concrete implementation of the Unit of Work pattern that manages a session
        with a database and coordinates transaction commit and rollback.
        It also manages repository instances for different entities.
    """

    def __init__(self, session_factory: async_sessionmaker):
        """
            Initializes the UnitOfWork with a session factory.
            The session factory is responsible for creating new sessions.
        """
        self.session_factory = session_factory
        self.repositories = {}

    async def __aenter__(self):
        """
            Creates a new database session and starts the unit of work.
            Returns the UnitOfWork instance to be used within the 'async with' block.
        """
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
           Commits or rolls back the transaction depending on the outcome of the operations.
           If an exception occurred, the transaction is rolled back, otherwise, it's committed.
           Closes the session when done.
       """
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        """
            Commits the current transaction, making all changes in the session permanent.
        """
        await self.session.commit()

    async def rollback(self):
        """
            Rolls back the transaction, undoing any changes made during the session.
        """
        await self.session.rollback()

    def set_repository(self, name, repository_class):
        """
            Registers a repository by name, allowing easy access to it later.
        """
        if name not in self.repositories:
            self.repositories[name] = repository_class

    def __getattr__(self, name):
        """
            Dynamically retrieves the repository associated with the given name.
            If no repository is found, raises an AttributeError.
        """
        if name in self.repositories:
            return self.repositories[name](self.session)
        raise AttributeError(f"'UnitOfWork' object has no attribute '{name}'")
