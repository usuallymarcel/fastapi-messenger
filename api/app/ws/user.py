from app.crud.groups import get_group_by_id
from app.crud.group_members import get_all_group_memberships_by_user_id
from app.crud.friend_request import get_received_friend_requests, get_sent_friend_requests
from app.crud.friends import get_all_friends_by_id
from app.crud.messages import get_unread_message_count_by_friend
from app.crud.users import get_user_by_id
from sqlalchemy.orm import Session
from app.ws.manager import ConnectionManager


async def load_user_data(manager: ConnectionManager, db: Session, user_id: int):
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
        
    groups_memberships = get_all_group_memberships_by_user_id(db, user_id) 

    for membership in groups_memberships:
        group = get_group_by_id(db, membership.group_id)

        await manager.send(user_id, 
                           {
                               "type": "load_group",
                               "group_id": group.id,
                               "group_name": group.name,
                               "group_user_id": membership.id,
                               "is_admin": membership.is_admin,
                           })