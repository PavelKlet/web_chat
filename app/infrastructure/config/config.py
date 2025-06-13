from pydantic_settings import BaseSettings
from fastapi.templating import Jinja2Templates


class Settings(BaseSettings):
    db_user: str
    db_pass: str
    db_host: str
    db_port: int
    db_name: str

    secret: str

    redis_host: str = "localhost"
    redis_port: int = 6379

    mongo_user: str
    mongo_pass: str
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db_name: str

    email_username: str
    email_host: str
    email_port: int
    email_password: str

    @property
    def postgresql_url(self) -> str:

        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def mongo_uri(self) -> str:
        return (
            f"mongodb://{self.mongo_user}:{self.mongo_pass}@"
            f"{self.mongo_host}:{self.mongo_port}/"
            f"{self.mongo_db_name}?authSource=admin"
        )


settings = Settings()
templates = Jinja2Templates(directory="frontend/html")

