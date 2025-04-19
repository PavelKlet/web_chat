import json

from fastapi import WebSocket, Request, APIRouter, Depends
from fastapi.exception_handlers import HTTPException
from fastapi.websockets import WebSocketDisconnect

from app.infrastructure.auth.auth_manager import AuthManager, get_auth_manager
from app.infrastructure.config import templates
from .dependencies import ChatServiceDep, UserServiceDep
from app.infrastructure.websocket.websocket_manager import websocket_manager

router = APIRouter()


@router.websocket("/ws/{user_id_recipient}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id_recipient: int,
    chat_service: ChatServiceDep,
    user_service: UserServiceDep,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """
        Handles real-time WebSocket communication for a chat between users.
        Establishes a connection, manages incoming messages, and handles disconnections.
        """

    (room_connections,
     room,
     user,
     recipient
     ) = await websocket_manager.connect(
        websocket,
        user_id_recipient,
        chat_service,
        user_service,
        auth_manager
    )
    try:
        while True:
            raw_text = await websocket.receive_text()

            if not raw_text.strip():
                continue

            data = f"{user.username}: {raw_text}"
            data = data[:1024]
            message_data = {
                "text": data,
                "avatarUrl": user.profile.avatar
            }
            await websocket_manager.send_message(room_connections,
                                                 message_data,
                                                 chat_service,
                                                 room.id,
                                                 user
                                                 )
    except WebSocketDisconnect:
        room_connections.remove(websocket)
        if len(room_connections) == 0:
            await websocket_manager.delete_room(room.id)


@router.get("/get/chat/")
async def get_chat(
        request: Request,
        recipient_id: int,
        ):
    """
        Renders the chat page for the specified recipient.
    """

    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/getcookies/")
def get_access_token_cookie(request: Request):
    """
        Retrieves the access token from the request cookies.
        Raises an HTTP exception if the token is not found.
    """

    token = request.cookies.get('access_token')
    if token:
        return token

    raise HTTPException(status_code=401, detail="Access token not found")
