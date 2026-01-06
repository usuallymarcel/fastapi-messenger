from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.models.messages import Message
from datetime import datetime

def get_messages_for_user_and_friend(
    db: Session, 
    user_id: int, 
    friend_id: int,
    before: datetime | None = None,
    take: int = 10,
):
    query = db.query(Message).filter(
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

    if before:
        query = query.filter(Message.created_at < before)

    messages = (
        query
        .order_by(Message.created_at.desc())
        .limit(take)
        .all()
    )

    message_ids = [
        m.id for m in messages
        if m.sender_id == friend_id and not m.read
    ]

    if message_ids:
        (
            db.query(Message)
            .filter(Message.id.in_(message_ids))
            .update({Message.read: True}, synchronize_session=False)
        )
    
    db.commit()

    return list(reversed(messages))

def get_unread_message_count_by_friend(db: Session, user_id: int, friend_id: int) -> int:
    return (db.query(Message).filter(Message.sender_id == friend_id,
                             Message.receiver_id == user_id,
                             Message.read == False).count())

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

def update_message_read_by_id(db: Session, user_id: int, message_id: int):
    db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.id == message_id,
        Message.read == False,
    ).update(
        {Message.read: True},
        synchronize_session=False,
    )
    db.commit()

def update_message_read(db: Session, message_id: int, read_status: bool):
    message = db.query(Message).filter(Message.id == message_id).first()
    if message:
        message.read = read_status

        db.commit()
