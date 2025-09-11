from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String

from src.db import Base

class FasilitiesModel(Base):
    __tablename__ = "fasilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))

class RoomsFasilitiesModel(Base):
    __tablename__ = "rooms_fasilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    rooms_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    fasilities_id: Mapped[int] = mapped_column(ForeignKey("fasilities.id"))
