from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.friend_request import FriendRequest, FriendStatus

def get_friend_request_by_id(db: Session, user_id: int, friend_id: int):
    return (
        db.query(FriendRequest)
        .filter(
            or_(
                and_(
                    FriendRequest.sender_id == user_id,
                    FriendRequest.receiver_id == friend_id,
                ),
                and_(
                    FriendRequest.sender_id == friend_id,
                    FriendRequest.receiver_id == user_id,
                ),
            )
        )
        .first()
    )

def get_sent_friend_requests(db: Session, user_id: int):
    return (
        db.query(FriendRequest)
        .filter(
            and_(
                FriendRequest.sender_id == user_id,
                FriendRequest.status == FriendStatus.PENDING,
            )
        )
        .all()
    )

def get_received_friend_requests(db: Session, user_id: int):
    return (
        db.query(FriendRequest)
        .filter(
            and_(
                FriendRequest.receiver_id == user_id,
                FriendRequest.status == FriendStatus.PENDING,
            )
        )
        .all()
    )

def get_friend_request(db: Session, request_id: int):
    return db.query(FriendRequest).filter(FriendRequest.id == request_id).first()

def create_friend_request(db: Session, user_id: int, friend_id: int):
    friendRequest = FriendRequest(
                sender_id=user_id,
                receiver_id=friend_id,
    )
    db.add(friendRequest)
    db.commit()
    db.refresh(friendRequest)
    return friendRequest

def update_friend_request_status(db: Session, request: FriendRequest, status: FriendStatus):
    if request:
        request.status = status
        db.commit()

        return request