from sqlalchemy import String, Integer, TIMESTAMP, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.database import Base


class GroupMessage(Base):
    __tablename__ = "group_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False
    )

    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        String(2000),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index(
            "ix_group_messages_group_created",
            "group_id",
            "created_at"
        ),
    )