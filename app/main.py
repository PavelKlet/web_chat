from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exception_handlers import RequestValidationError

from app.infrastructure.utils.redis_utils.redis_utils import redis_utils
from app.infrastructure.config import templates
from .api.chat import router as chat_router
from .api.users import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_utils.pool_disconnect()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def http_exception_handler(request, exc):
    return templates.TemplateResponse(
        "error.html",
        {"request": request},
        status_code=400
    )

app.include_router(user_router, tags=["users"])
app.include_router(chat_router, tags=["chat"])

