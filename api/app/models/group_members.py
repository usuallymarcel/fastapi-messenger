from sqlalchemy import Integer, TIMESTAMP, ForeignKey, func, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.database import Base

class GroupMember(Base):
    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(primary_key=True)

    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    is_admin: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )

    joined_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
    )

    