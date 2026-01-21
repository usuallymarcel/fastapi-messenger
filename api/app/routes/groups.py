from app.utils.session_token import get_session_from_request
from app.crud.group_members import get_membership_by_group_id_user_id
from app.dependencies import get_db
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.crud.group_invite import create_group_invite
from app.schemas.group_invite import GroupInviteSchema
from app.config import settings


router = APIRouter(prefix="/groups", tags=["groups"])

@router.post('/{group_id}/invite')
async def create_invite(request: Request, data: GroupInviteSchema, group_id: int, db: Session = Depends(get_db)):
    session = get_session_from_request(db, request)
    membership = get_membership_by_group_id_user_id(db, session.user_id, group_id)
    if not membership:
        return {"Error": "user is not a member of the group"}
    group_invite = create_group_invite(db, session.user_id, data.max_uses, group_id)
    
    return {"invite_link": f"""{settings.api_url}/groups/join/{group_invite.token}"""}