from app.crud.users import get_user_by_id
from sqlalchemy.orm import Session
from app.crud.friend_request import create_friend_request, get_friend_request, update_friend_request_status, get_friend_request_by_id, get_received_friend_requests, get_sent_friend_requests
from app.crud.friends import create_friend
from app.crud.users import get_user_by_id
from app.models.friend_request import FriendRequest, FriendStatus
from app.ws.manager import ConnectionManager

async def handle_friend_request(manager: ConnectionManager, db: Session, sender_id: int, data: dict):
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
    

async def handle_friend_accept(manager: ConnectionManager, db: Session, user_id: int, data: dict):
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


async def handle_friend_reject(manager: ConnectionManager, db: Session, user_id: int, data: dict):
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
