from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

router = APIRouter(prefix="/groups", tags=["groups"])

@router.post('/{group_id}/invite')
async def create_invite(group_id: int):
    return {"group_id": group_id}