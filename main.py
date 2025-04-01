from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import RequestValidationError

# from users import views as register_router
from infrastructure.utils.redis_utils import redis_utils
# from chat import views as chat_router
from infrastructure.config import templates
from api.chat import router as chat_router
from api.users import router as user_router


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

app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(user_router, tags=["users"])
app.include_router(chat_router, tags=["chat"])

