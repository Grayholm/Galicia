from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date

from src.db import Base

class UsersModel(Base):
    __tablename__ = "users"


    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    nickname: Mapped[str] = mapped_column(String(100))
    birth_day: Mapped[date] = mapped_column(Date())
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))