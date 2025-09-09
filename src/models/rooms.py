from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from src.db import Base


class RoomsModel(Base):
    __tablename__ = 'rooms'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey('hotels.id'))
    title: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]