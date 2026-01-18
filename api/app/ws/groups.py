from app.crud.users import get_user_by_id
from app.crud.group_messages import create_group_message, get_messages_by_group
from app.crud.group_members import create_group_member, get_group_members, get_membership_by_group_id_user_id
from app.crud.groups import create_group
from sqlalchemy.orm import Session
from app.ws.manager import ConnectionManager
from app.utils.format_time import format_to_nz_time

async def handle_group_create(manager: ConnectionManager, db: Session, user_id: int, data: dict):
    try:
        group_name = data["group_name"]

        if not group_name:
            return
    
        is_private = True
        if 'group_is_private' in data:
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
        
async def handle_get_group_messages(manager: ConnectionManager, db: Session, user_id: int, data: dict):
    try:
        group_id = data["group_id"]

        if not group_id:
            return
        
        group_id = int(group_id)

        group_member = get_membership_by_group_id_user_id(db, user_id, group_id)
        if not group_member:
            await manager.send(user_id, 
                               {
                                   "type": "Error",
                                   "message": "invalid group id"
                               })
            return

        group_messages = get_messages_by_group(db, group_member.group_id)

        for message in group_messages:
            sender = get_user_by_id(db, message.sender_id)
            await manager.send(user_id, 
                               {
                                   "type": "group_message_received",
                                   "content": f"{format_to_nz_time(message.created_at)} - {sender.email}: {message.content}",
                                   "from": group_id
                               })

    except:
        await manager.send(user_id, 
                           {
                                "type": "Error",
                                "message": "Couldn't Get Group Messages"
                           })

async def handle_group_message(manager: ConnectionManager, db: Session, user_id: int, data: dict):
    try:
        group_id = data["group_id"]
        group_message = data["group_message"]

        group_id = int(group_id)
        group_message = str(group_message)

        group_member = get_membership_by_group_id_user_id(db, user_id, group_id)

        if not group_member:
            await manager.send(user_id, 
                    {
                        "type": "Error",
                        "message": "invalid group id"
                    })
            return
        
        message = create_group_message(db, group_id, user_id, group_message)

        sender = get_user_by_id(db, user_id)

        group_members = get_group_members(db, group_id)

        # await manager.send(user_id, 
        #                    {
        #                        "type": "group_message_sent",
        #                        "content": f"{format_to_nz_time(message.created_at)} - {sender.email}: {message.content}",
        #                        "to": group_id
        #                    })
        
        for member in group_members:
            # if (member.id == user_id): continue
            
            await manager.send(member.user_id, 
                               {
                                   "type": "group_message_received",
                                   "content": f"{format_to_nz_time(message.created_at)} - {sender.email}: {message.content}",
                                   "from": group_id,
                               })

    except:
        await manager.send(user_id, 
                          {
                              "type": "Error",
                              "Message": "Couldn't Send Group Message"
                          })

    