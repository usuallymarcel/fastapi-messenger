from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Response, Request
from pathlib import Path
import os
from app.crud.messages import create_message
from app.dependencies import get_db
from app.utils.session_token import get_session_from_websocket
from app.crud.users import get_user_by_id
from sqlalchemy.orm import Session
from app.crud.friend_request import create_friend_request, get_friend_request, update_friend_request_status, get_friend_request_by_id, get_received_friend_requests, get_sent_friend_requests
from app.crud.friends import create_friend, get_all_friends_by_id, get_friend_by_id
from app.crud.users import get_user_by_id
from app.crud.messages import get_messages_for_user_and_friend, get_unread_message_count_by_friend, update_message_read_by_id
from app.models.friend_request import FriendRequest, FriendStatus
from zoneinfo import ZoneInfo

router = APIRouter(prefix="/ws", tags=["ws"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send(self, user_id: int, message: dict):
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()
messages = []

@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):

    session = await get_session_from_websocket(db, websocket)

    if not session:
        await websocket.close(code=1008)
        return
    
    await manager.connect(session.user_id, websocket)
    await load_user_data(db, session.user_id)
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
            await handle_friend_request(db, user_id, data)
        case "friend_accept":
            await handle_friend_accept(db, user_id, data)
        case "friend_reject":
            await handle_friend_reject(db, user_id, data)
        case "message":
            await handle_message(db, user_id, data)
        case "get_messages":
            await handle_get_messages(db, user_id, data)
        case "message_read":
            await handle_read_message(db, user_id, data)
        case _:
            raise ValueError("Unknown event type")
        
async def handle_friend_request(db: Session, sender_id: int, data: dict):
    to_user_id = data["to_user_id"]

    if not to_user_id:
        return
    
    receiver_id = int(to_user_id)

    request = get_friend_request_by_id(db, sender_id, receiver_id)
    if request:
        await manager.send(sender_id,
                           {
                               "type": "Error",
                               "message": "Friend Request Already Exists",
                           })
        return

    request = create_friend_request(db, sender_id, receiver_id)
    user = get_user_by_id(db, sender_id)
    receiver = get_user_by_id(db, receiver_id)

    await manager.send(receiver_id, 
                       {
                           "type": "friend_request_received",
                           "from_user_id": sender_id,
                           "request_id": request.id,
                           "username": user.email,
                       })
    
    await manager.send(sender_id, 
                    {
                        "type": "friend_request_sent",
                        "to_user_id": request.receiver_id,
                        "request_id": request.id,
                        "username": receiver.email,
                    })
    

async def handle_friend_accept(db: Session, user_id: int, data: dict):
    request_id = data["request_id"]

    request = get_friend_request(db, request_id)

    if request.receiver_id != user_id:
        return
    
    update_friend_request(db, request, FriendStatus.ACCEPTED)

    sender = get_user_by_id(db, request.sender_id)
    receiver = get_user_by_id(db, request.receiver_id)

    await manager.send(
        request.sender_id,
        {
            "type": "friend_request_accepted",
            "request_id": request.id,
            "user_id": request.receiver_id,
            "username": receiver.email
        }
    )
    await manager.send(
        request.receiver_id,
        {
            "type": "friend_request_accepted",
            "request_id": request.id,
            "user_id": request.sender_id,
            "username": sender.email
        }
    )

async def handle_friend_reject(db: Session, user_id: int, data: dict):
    request_id = data["request_id"]

    request = get_friend_request(db, request_id)


    if not request or request.receiver_id != user_id:
        return
    
    update_friend_request(db, request, FriendStatus.REJECTED)

    await manager.send(
        request.sender_id,
        {
            "type": "friend_request_rejected",
            "request_id": request.id
        }
    )

    await manager.send(
        request.receiver_id,
        {
            "type": "friend_request_rejected",
            "request_id": request.id,
        }
    )
    

def update_friend_request(db: Session, request: FriendRequest, status: FriendStatus):
    update_friend_request_status(db, request, status)

    if status == FriendStatus.ACCEPTED:
        create_friend(db, request.sender_id, request.receiver_id)

async def load_user_data(db: Session, user_id: int):
    requests = get_sent_friend_requests(db, user_id)

    for request in requests:
        receiver = get_user_by_id(db, request.receiver_id)
        await manager.send(user_id, 
                    {
                        "type": "friend_request_sent",
                        "to_user_id": request.receiver_id,
                        "request_id": request.id,
                        "username": receiver.email,
                    })
        
    received_requests = get_received_friend_requests(db, user_id)

    for request in received_requests:
        sender = get_user_by_id(db, request.sender_id)
        await manager.send(user_id, 
                    {
                        "type": "friend_request_received",
                        "from_user_id": request.sender_id,
                        "request_id": request.id,
                        "username": sender.email,
                    })
    friends = get_all_friends_by_id(db, user_id)

    for friend in friends:
        friend_id = friend.user_id_1

        if friend.user_id_1 == user_id:
            friend_id = friend.user_id_2

        count = get_unread_message_count_by_friend(db, user_id, friend_id)

        friend = get_user_by_id(db, friend_id)
        await manager.send(user_id,
                           {
                               "type": "load_friend",
                               "user_id": friend_id,
                               "username": friend.email,
                               "unread_count": count,
                           })
        
async def handle_get_messages(db: Session, user_id: int, data: dict):
    friend_id = data["friend_id"]

    if not friend_id:
        return
    
    try:
        friend_id = int(friend_id)
    except:
        await manager.send(user_id,
                           {
                               "type": "Error",
                               "message": "invalid friend id",
                           })
        return

    friend = get_friend_by_id(db, user_id, friend_id)

    if not friend:
        await manager.send(user_id,
                           {
                               "type": "Error",
                               "message": "No friend with that ID",
                           })
        return


    messages = get_messages_for_user_and_friend(db, user_id, friend_id)

    for message in messages:
        nz_time = message.created_at.astimezone(ZoneInfo("Pacific/Auckland"))
        formatted_time = nz_time.strftime("%d %b %Y %H:%M") 

        sender = get_user_by_id(db, message.sender_id)
        receiver = get_user_by_id(db, message.receiver_id)
        await manager.send(user_id,
                            {
                                "type": "message_sent",
                                "content": f"{formatted_time} - {sender.email}: {message.content}",
                                "to": receiver.id  
                        })

async def handle_read_message(db: Session, user_id: int, data: dict):
    try:
        message_id = int(data["message_id"])
    except:
        await manager.send(user_id,
                    {
                        "type": "Error",
                        "message": "invalid message id",
                    })
        return
    update_message_read_by_id(db, user_id, message_id)
        
async def handle_message(db: Session, user_id: int, data: dict):
    to_user_id = data["to_user_id"]
    content = data["content"]

    if not to_user_id or not content:
        return
    
    try:
        to_user_id = int(to_user_id)
    except:
        await manager.send(user_id,
                           {
                               "type": "Error",
                               "message": "invalid user id",
                           })
        return

    friend = get_friend_by_id(db, user_id, to_user_id)

    if not friend:
        await manager.send(user_id,
                           {
                               "type": "Error",
                               "message": "No friend with that ID",
                           })
        return
    
    message = create_message(db, user_id, to_user_id, content)
    sender = get_user_by_id(db, user_id)

    nz_time = message.created_at.astimezone(ZoneInfo("Pacific/Auckland"))
    formatted_time = nz_time.strftime("%d %b %Y %H:%M") 

    await manager.send(user_id,
                        {
                            "type": "message_sent",
                            "content": f"{formatted_time} - {sender.email}: {message.content}",
                            "to": to_user_id  
                       })
    
    await manager.send(to_user_id,
                        {
                            "type": "message_received",
                            "content": f"{formatted_time} - {sender.email}: {message.content}",
                            "from": sender.id,
                            "message_id": message.id,  
                       })