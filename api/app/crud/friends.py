from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.friends import Friend

def get_friend_by_id(db: Session, user_id: int, friend_id: int):
    uid_1, uid_2 = sorted((user_id, friend_id))
    return (
        db.query(Friend)
        .filter(
            Friend.user_id_1 == uid_1,
            Friend.user_id_2 == uid_2
        )
        .first()
    )

def create_friend(db: Session, user_id: int, friend_id: int):
    uid_1, uid_2 = sorted((user_id, friend_id))
    friend = Friend(
                user_id_1=uid_1,
                user_id_2=uid_2)
    db.add(friend)
    db.commit()
    db.refresh(friend)
    return friend

def get_all_friends_by_id(db: Session, user_id: int):
    return db.query(Friend).filter(or_(Friend.user_id_1 == user_id, Friend.user_id_2 == user_id)).all()

