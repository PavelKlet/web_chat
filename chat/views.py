import json

from fastapi import WebSocket, Request, APIRouter, Depends
from fastapi.exception_handlers import HTTPException
from fastapi.websockets import WebSocketDisconnect

from core.config import templates
from .crud import save_message
from .websocket_manager import websocket_manager
from users.crud import session_dependency, RepositoryUser
router = APIRouter()


@router.websocket("/ws/{user_id_recipient}")
async def websocket_endpoint(
        websocket: WebSocket,
        user_id_recipient: int,
        session: RepositoryUser = Depends(session_dependency.get_session)
):
    room_connections, room, user, recipient = await websocket_manager.connect(
        websocket,
        user_id_recipient,
        session
    )
    try:
        while True:
            data = f"{user.username}: " + await websocket.receive_text()
            data = data[:1024]
            data = {
                "text": data,
                "avatarUrl": user.profile.avatar
            }
            await save_message(json.dumps(data), room.id)
            await websocket_manager.send_message(room_connections, data)
    except WebSocketDisconnect:
        room_connections.remove(websocket)
        if len(room_connections) == 0:
            await websocket_manager.delete_room(room.id)


@router.get("/get/chat/")
async def get_chat(
        request: Request,
        recipient_id: int,
        ):
    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/getcookies/")
def get_access_token_cookie(request: Request):
    token = request.cookies.get('access_token')
    if token:
        return token

    raise HTTPException(status_code=401, detail="Access token not found")
