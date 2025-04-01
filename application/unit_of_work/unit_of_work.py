from abc import ABC, abstractmethod


class IUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.repositories = {}

    async def __aenter__(self):
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    def set_repository(self, name, repository_class):
        if name not in self.repositories:
            self.repositories[name] = repository_class

    def __getattr__(self, name):
        if name in self.repositories:
            return self.repositories[name](self.session)
        raise AttributeError(f"'UnitOfWork' object has no attribute '{name}'")
