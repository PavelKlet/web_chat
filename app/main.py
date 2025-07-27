import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.infrastructure.utils.redis_utils.redis_utils import redis_utils
from app.infrastructure.config.config import templates
from .api.chat import router as chat_router
from .api.users import router as user_router
from .application.services.websocket.websocket_manager import websocket_manager
from .infrastructure.config.database import init_mongo, mongo_db
from .infrastructure.utils.tasks import start_listener_with_restart


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mongo()

    listener_task = asyncio.create_task(
        start_listener_with_restart(
            redis_utils=redis_utils,
            rooms=websocket_manager.rooms,
            delete_room_callback=websocket_manager.delete_room
        )
    )

    yield

    await redis_utils.pool_disconnect()
    mongo_db.client.close()

    listener_task.cancel()
    try:
        await listener_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def http_exception_handler(request, exc):
    """
       Handles request validation errors raised when incoming request data (query params,
       form fields, body, etc.) do not conform to the expected Pydantic models or type hints.

       If the request comes from a browser (typically expecting HTML), this handler returns
       a custom HTML error page using the 'error.html' Jinja2 template.

       Parameters:
           request (Request): The incoming request that triggered the validation error.
           exc (RequestValidationError): The exception instance containing details about validation failure.

       Returns:
           TemplateResponse: A rendered HTML error page with status code 400.
       """
    return templates.TemplateResponse(
        "error.html",
        {"request": request},
        status_code=400
    )

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handles general HTTP exceptions, including 401, 404 and others.
    """
    accept_header = request.headers.get("accept", "")

    if exc.status_code == 404:
        if "text/html" in accept_header:
            return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
        else:
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.get("/")
async def redirect_to_profile():
    """
    Redirects the root URL to the profile page.
    """
    return RedirectResponse(url="/profile")

app.include_router(user_router, tags=["users"])
app.include_router(chat_router, tags=["chat"])

