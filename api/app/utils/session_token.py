from fastapi import Request, HTTPException, WebSocket
from app.models.session_token import Session_Token
from sqlalchemy.orm import Session
from app.crud.session_tokens import get_session_by_id
from datetime import datetime, timezone, timedelta

def get_session_from_request(db: Session, request: Request) -> Session_Token:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid Session")
    
    if session.expires_at < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        db.refresh()
        raise HTTPException(status_code=401, detail="Session expired")
    
    return session

def refresh_session_if_needed(db: Session, session: Session_Token):
    if session.expires_at - datetime.now(timezone.utc) < timedelta(hours=4):
        session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        db.commit()

async def get_session_from_websocket(db: Session, websocket: WebSocket):
    session_id = websocket.cookies.get("session_id")

    if not session_id:
        return None
    
    session = get_session_by_id(db, session_id)
    if not session:
        return None
    
    if session.expires_at < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        return None
    
    refresh_session_if_needed(db, session)

    return session