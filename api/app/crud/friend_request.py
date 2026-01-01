from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.friend_request import FriendRequest

def get_friend_request_by_id(db: Session, user_id: int, friend_id: int):
    uid_1, uid_2 = sorted((user_id, friend_id))
    return (
        db.query(FriendRequest)
        .filter(
            FriendRequest.user_id_1 == uid_1,
            FriendRequest.user_id_2 == uid_2
        )
        .first()
    )

def create_friend_request(db: Session, user_id: int, friend_id: int):
    uid_1, uid_2 = sorted((user_id, friend_id))
    friendRequest = FriendRequest(
                sender_id=user_id,
                user_id_1=uid_1,
                user_id_2=uid_2)
    db.add(friendRequest)
    db.commit()
    db.refresh(friendRequest)
    return friendRequest

