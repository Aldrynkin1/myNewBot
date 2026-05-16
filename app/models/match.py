from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user1_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user2_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    active: Mapped[bool] = mapped_column(Boolean, default=True)