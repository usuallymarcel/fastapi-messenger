from pathlib import Path
from app.utils.session_token import get_session_from_request, is_session_valid
from app.crud.group_members import create_group_member, get_membership_by_group_id_user_id
from app.dependencies import get_db
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, Response, RedirectResponse
from sqlalchemy.orm import Session
from app.crud.group_invite import create_group_invite, get_group_invite_by_token, update_group_invite_uses_by_token
from app.schemas.group_invite import GroupInviteSchema
from app.config import settings


router = APIRouter(prefix="/groups", tags=["groups"])
BASE_DIR = Path(__file__).resolve().parent

@router.post('/{group_id}/invite')
async def create_invite(request: Request, data: GroupInviteSchema, group_id: int, db: Session = Depends(get_db)):
    session = get_session_from_request(db, request)
    membership = get_membership_by_group_id_user_id(db, session.user_id, group_id)
    if not membership:
        return {"Error": "user is not a member of the group"}
    group_invite = create_group_invite(db, session.user_id, data.max_uses, group_id)
    
    return {"invite_link": f"""{settings.api_url}/groups/join/{group_invite.token}"""}

@router.get('/join/{invite_token}')
async def join_group(request: Request, invite_token: str, db: Session = Depends(get_db)):
    session_valid = is_session_valid(db, request)

    if not session_valid:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("pending_invite", invite_token, httponly=True)

        return response
    
    session = get_session_from_request(db, request)

    group_invite = get_group_invite_by_token(db, invite_token)
    
    membership = get_membership_by_group_id_user_id(db, session.user_id, group_invite.group_id)

    if membership:
        return RedirectResponse(url="/chat", status_code=302)

    create_group_member(db, group_invite.group_id, session.user_id)

    update_group_invite_uses_by_token(db, group_invite.uses_count + 1, invite_token)

    return RedirectResponse(url="/chat", status_code=302)
