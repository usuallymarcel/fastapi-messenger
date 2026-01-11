from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.group_members import GroupMember

def create_group_member(db: Session, group_id: int, user_id: int, is_admin: bool = False) -> GroupMember:
  groupMember = GroupMember(group_id=group_id,
                            user_id=user_id,
                            is_admin=is_admin
                            )
  
  db.add(groupMember)
  db.commit()

  return groupMember

def get_group_members(db: Session, group_id: int) -> list[GroupMember]:
  return db.query(GroupMember).filter(group_id == group_id).all()