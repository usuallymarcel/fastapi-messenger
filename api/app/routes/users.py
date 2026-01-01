from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.user import UserCreate, UserRead, credentials
from app.crud.users import get_user_by_email, create_user, get_users
from app.crud.session_tokens import create_session
from app.utils.credentials import verify_password
from app.utils.session_token import get_session_from_request, refresh_session_if_needed

router = APIRouter(prefix="/users", tags=["users"])

# @router.post("/", response_model=UserRead)
# def create(user: UserCreate, db: Session = Depends(get_db)):
#     if get_user_by_email(db, user.email):
#         raise HTTPException(status_code=400, detail="Email already exists")
    
#     return create_user(db, user.email, user.name)

@router.get("/")
def get_all_users(db: Session = Depends(get_db)):
    return get_users(db)

@router.post("/login")
def login(data: credentials, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)

    if not user:
        return {"verified": False, "message": "No user with that email"}

    if not verify_password(data.password, user.hashed_password, user.salt, user.iterations):
        return {"verified": False, "message": "Incorrect password"}
    
    session_token = create_session(db, user.id)

    response.set_cookie(
        key="session_id",
        value=session_token.id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24
    )
    
    return {"verified": True, "message": "Password correct"}

@router.post("/sign_up")
def sign_up(data: credentials, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    
    if user:
        return {"created": False, "message": "Email already exists"}
    
    user = create_user(db, data.email, "pissname", data.password)

    session_token = create_session(db, user.id)

    response.set_cookie(
        key="session_id",
        value=session_token.id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24
    )

    return {"created": True, "message": "Account creation Succesful"}
    
@router.get("/check_session")
def check_session(request: Request, db: Session = Depends(get_db)):
    session = get_session_from_request(db, request)
    refresh_session_if_needed(db, session)
    return {"verified": True, "message": "Session valid"}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    session = get_session_from_request(db, request)
    db.delete(session)
    db.commit()

    response.delete_cookie("session_id")
    return {"ok": True, "logged out": True}