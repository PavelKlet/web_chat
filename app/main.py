from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exception_handlers import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.utils.redis_utils.redis_utils import redis_utils
from app.infrastructure.config import templates
from .api.chat import router as chat_router
from .api.users import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_utils.pool_disconnect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.exception_handler(RequestValidationError)
async def http_exception_handler(request, exc):
    return templates.TemplateResponse(
        "error.html",
        {"request": request},
        status_code=400
    )

@app.get("/")
async def redirect_to_profile():
    """
    Redirects the root URL to the profile page.
    """
    return RedirectResponse(url="/profile")

app.include_router(user_router, tags=["users"])
app.include_router(chat_router, tags=["chat"])

