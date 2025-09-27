import typing
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String

from src.db import Base

if typing.TYPE_CHECKING:
    from src.models import HotelsModel


class ImagesModel(Base):
    __tablename__ = "images"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    hotels: Mapped[list["HotelsModel"]] = relationship(
        "HotelsModel",
        back_populates="images",
        secondary="hotels_images",
    )


class HotelsImagesModel(Base):
    __tablename__ = "hotels_images"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"))
