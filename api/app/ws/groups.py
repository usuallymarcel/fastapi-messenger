from app.crud.group_members import create_group_member
from app.crud.groups import create_group
from app.crud.users import get_user_by_id
from sqlalchemy.orm import Session
from app.crud.friend_request import create_friend_request, get_friend_request, update_friend_request_status, get_friend_request_by_id, get_received_friend_requests, get_sent_friend_requests
from app.crud.friends import create_friend
from app.crud.users import get_user_by_id
from app.models.friend_request import FriendRequest, FriendStatus
from app.ws.manager import ConnectionManager

async def handle_group_create(manager: ConnectionManager, db: Session, user_id: int, data: dict):
    try:
        group_name = data["group_name"]
        

        if not group_name:
            return
    
        is_private = True
        if data["group_is_private"]:
            is_private = data["group_is_private"]
        

        group = create_group(db, group_name, user_id, is_private)
        group_member = create_group_member(db, group.id, user_id, True)
        await manager.send(user_id,
                          {
                              "type": "load_group",
                              "group_name": group.name,
                              "group_id": group.id,
                              "is_admin": group_member.is_admin,
                              "group_user_id": group_member.id
                          })
    except:
        await manager.send(user_id,
                    {
                        "type": "Error",
                        "message": "Couldn't Create Group"
                    })

async def handle_friend_request(manager: ConnectionManager, db: Session, sender_id: int, data: dict):
    to_user_id = data["to_user_id"]

    if not to_user_id:
        return
    
    receiver_id = int(to_user_id)

    try:
        receiver = get_user_by_id(db, receiver_id)
        if not receiver:
            return
    except:
        await manager.send(sender_id,
                           {
                               "type": "Error",
                               "message": "Couldn't Get friend"
                           })

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
    