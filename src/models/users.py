from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.db import Base

class UsersModel(Base):
    __tablename__ = "users"


    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    nickname: Mapped[str] = mapped_column(String(100))
    birth_day: Mapped[int]
    email: Mapped[str] = mapped_column(String(200))
    hashed_password: Mapped[str] = mapped_column(String(200))