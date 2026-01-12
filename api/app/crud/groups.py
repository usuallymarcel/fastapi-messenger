from sqlalchemy.orm import Session
from app.models.groups import Group

def create_group(db: Session, name: str, created_by: int, is_private: bool = True) -> Group:
    group = Group(
        name = name,
        created_by=created_by,
        is_private=is_private
    )
    db.add(group)
    db.commit()

    return group

def get_group_by_id(db: Session, id: int) -> Group:
    return db.query(Group).filter(Group.id == id).first()

def update_group_name(db: Session, id: int, name: str) -> None:
    db.query(Group).filter(Group.id == id).update(Group.name == name)
    db.commit()

def update_is_private(db: Session, id: int, is_private: bool) -> None:
    db.query(Group).filter(Group.id == id).update(Group.is_private == is_private)
    db.commit()

def delete_group_by_id(db: Session, id: int) -> None:
    db.query(Group).filter(Group.id == id).delete()
    db.commit()