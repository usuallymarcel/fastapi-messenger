from app.ws.groups import handle_group_create
from app.ws.friends import handle_friend_accept, handle_friend_reject, handle_friend_request
from app.ws.messages import handle_get_messages, handle_message, handle_read_message
from app.ws.user import load_user_data
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pathlib import Path
from app.dependencies import get_db
from app.utils.session_token import get_session_from_websocket
from sqlalchemy.orm import Session
from app.ws.manager import ConnectionManager

router = APIRouter(prefix="/ws", tags=["ws"])


manager = ConnectionManager()
messages = []

@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):

    session = await get_session_from_websocket(db, websocket)

    if not session:
        await websocket.close(code=1008)
        return
    
    await manager.connect(session.user_id, websocket)
    await load_user_data(manager, db, session.user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await handle_ws_event(db, session.user_id, data)
    except WebSocketDisconnect:
        manager.disconnect(session.user_id)


async def handle_ws_event(db: Session, user_id: int, data: dict):
    event_type = data.get("type")

    match event_type:
        case "friend_request":
            await handle_friend_request(manager, db, user_id, data)
        case "friend_accept":
            await handle_friend_accept(manager, db, user_id, data)
        case "friend_reject":
            await handle_friend_reject(manager, db, user_id, data)
        case "message":
            await handle_message(manager, db, user_id, data)
        case "get_messages":
            await handle_get_messages(manager, db, user_id, data)
        case "message_read":
            await handle_read_message(manager, db, user_id, data)
        case "group_create":
            await handle_group_create(manager, db, user_id, data)
        case _:
            raise ValueError("Unknown event type")
        