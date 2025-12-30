from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.user import UserCreate, UserRead
from app.crud.users import get_user_by_email, create_user, get_users

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead)
def create(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    return create_user(db, user.email, user.name)

@router.get("/")
def get_all_users(db: Session = Depends(get_db)):
    return get_users(db)
