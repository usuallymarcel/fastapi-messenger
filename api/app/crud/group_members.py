from sqlalchemy.orm import Session
from sqlalchemy import and_
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
  return db.query(GroupMember).filter(GroupMember.group_id == group_id).all()

def get_all_group_memberships_by_user_id(db: Session, user_id: int) -> list[GroupMember]:
  return db.query(GroupMember).filter(GroupMember.user_id == user_id).all()

def get_membership_by_group_id_user_id(db: Session, user_id: int, group_id)-> GroupMember:
  return db.query(GroupMember).filter(
                                    and_
                                        (
                                        GroupMember.user_id == user_id,
                                        GroupMember.group_id == group_id  
                                        )
                                    ).first()