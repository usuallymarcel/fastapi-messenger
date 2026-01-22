import secrets
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.group_invite import GroupInvite

def create_group_invite(db: Session, user_id: int, max_uses: int, group_id: int) -> GroupInvite:
    token = secrets.token_urlsafe(32)
    groupInvite = GroupInvite(
        group_id=group_id,
        max_uses=max_uses,
        uses_count=0,
        token=token,
        created_by=user_id
    )

    db.add(groupInvite)
    db.commit()

    return groupInvite

def update_group_invite_uses_by_token(db: Session, uses: int, token: str) -> None:
    db.query(GroupInvite).filter(GroupInvite.token == token).update({GroupInvite.uses_count: uses})

    db.commit()

def get_group_invite_by_token(db: Session, token: str) -> GroupInvite:
    return db.query(GroupInvite).filter(GroupInvite.token == token).first()

def delete_group_invite_by_token(db: Session, token: str) -> None:
    db.query(GroupInvite).filter(GroupInvite.token == token).delete()
    db.commit()