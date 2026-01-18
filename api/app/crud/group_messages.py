from sqlalchemy.orm import Session
from app.models.group_messages import GroupMessage

def create_group_message(db: Session, group_id: int, sender_id: int, content: str) -> GroupMessage:
    group_message = GroupMessage(
        group_id= group_id,
        sender_id=sender_id,
        content=content,
    )

    db.add(group_message)
    db.commit()

    return group_message

def get_messages_by_group(db: Session, group_id: int, take: int = 10) -> list[GroupMessage]:
    messages = db.query(GroupMessage
                        ).filter(GroupMessage.group_id == group_id
                        ).order_by(GroupMessage.created_at.desc()).limit(take).all()
    
    return list(reversed(messages))

