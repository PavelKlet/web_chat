from pathlib import Path
from pydantic_settings import BaseSettings
from fastapi.templating import Jinja2Templates


BASE_DIRECTORY = Path(__file__).absolute().parent.parent


class Settings(BaseSettings):
    db_user: str
    db_pass: str
    db_host: str
    db_port: int
    db_name: str

    secret: str

    redis_host: str = "localhost"
    redis_port: int = 6379

    celery_user: str
    celery_password: str

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

    class Config:
        env_file = f"{BASE_DIRECTORY}/.env"


settings = Settings()
templates = Jinja2Templates(directory="frontend/html")

