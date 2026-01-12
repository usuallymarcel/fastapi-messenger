from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from app.crud.friends import get_friend_by_id
from app.crud.messages import create_message, get_messages_for_user_and_friend, update_message_read_by_id
from app.crud.users import get_user_by_id
from app.ws.manager import ConnectionManager

async def handle_get_messages(manager: ConnectionManager, db: Session, user_id: int, data: dict):
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
        
async def handle_message(manager: ConnectionManager, db: Session, user_id: int, data: dict):
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
    

async def handle_read_message(manager: ConnectionManager, db: Session, user_id: int, data: dict):
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