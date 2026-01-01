from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.credentials import hash_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, name: str, password: str):
    hashed_password, salt, iterations = hash_password(password)

    user = User(email=email, 
                name=name, 
                hashed_password=hashed_password, 
                salt=salt, 
                iterations=iterations)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session):
    return db.query(User).all()

# def get_email(email: str, db: Session):
#     return db.query(User).where(User.email == email).first()
