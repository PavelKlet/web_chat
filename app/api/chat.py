from typing import List

from fastapi import WebSocket, Request, APIRouter, Depends
from fastapi.exception_handlers import HTTPException
from fastapi.websockets import WebSocketDisconnect

from app.application.services.auth.auth_manager import AuthManager, get_auth_manager, get_current_user
from app.infrastructure.config.config import templates
from .dependencies import ChatServiceDep, UserServiceDep
from app.application.services.websocket.websocket_manager import websocket_manager
from .schemas.chat import ChatListItemSchema
from .schemas.users import UserRead

router = APIRouter()

@router.websocket("/ws/chat-list")
async def websocket_chat_list(
    websocket: WebSocket,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """
    WebSocket for updated chat list (new messages, latest messages update).
    """
    user = await websocket_manager.connect_chat_list(websocket, auth_manager)
    if not user:
        return

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in websocket_manager.chat_listeners:
            websocket_manager.chat_listeners.remove(websocket)

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

            message_data = {
                "username": user.username,
                "text": raw_text[:1024],
                "avatarUrl": user.profile.avatar
            }
            await websocket_manager.send_message(
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

@router.get("/api/chats", response_model=List[ChatListItemSchema])
async def get_user_chats(
    chat_service: ChatServiceDep,
    user_service: UserServiceDep,
    user: UserRead = Depends(get_current_user),
):
    """Gets a list of recent messages from chats"""
    rooms = await chat_service.get_user_room_ids(user.id)

    if not rooms:
        return []

    recipient_ids = [
        recipient_id if sender_id == user.id else sender_id
        for room_id, sender_id, recipient_id in rooms
    ]

    recipients = await user_service.get_users_with_profiles(recipient_ids)
    chat_list = await chat_service.get_user_chat_list(user.id, rooms, recipients)

    return chat_list

@router.get("/chats/")
async def get_index(request: Request):
    """Renders the chats."""

    return templates.TemplateResponse("chats.html", {"request": request})