from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.models.messages import Message

def get_messages_for_user_and_friend(db: Session, user_id: int, friend_id: int):
    return (
        db.query(Message)
        .filter(
            or_(
                and_(
                    Message.sender_id == user_id,
                    Message.receiver_id == friend_id,
                ),
                and_(
                    Message.sender_id == friend_id,
                    Message.receiver_id == user_id,
                ),
            )
        )
        .order_by(Message.created_at)
        .all()
    )

def create_message(db: Session, sender_id: int, receiver_id: int, content: str):
    message = Message(
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
