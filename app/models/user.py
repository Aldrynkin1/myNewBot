from sqlalchemy import String, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    state: Mapped[str] = mapped_column(String(20), default="idle")  
    # idle / waiting / chatting