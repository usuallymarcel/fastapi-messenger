import secrets
from sqlalchemy.orm import Session
from app.models.session_token import Session_Token
from datetime import datetime, timedelta, timezone

def create_session(db: Session, user_id: int, ip: str | None = None, user_agent: str | None = None):
    session_id = secrets.token_urlsafe(32)

    session_token = Session_Token(
        id=session_id,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        ip_address=ip,
        user_agent=user_agent
    )

    db.add(session_token)
    db.commit()
    db.refresh(session_token)
    return session_token

def get_session_by_id(db: Session, id: str):
    return db.query(Session_Token).filter(Session_Token.id == id).first()