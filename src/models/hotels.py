from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from src.db import Base


class HotelsModel(Base):
    __tablename__ = 'hotels'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    location: Mapped[str]

    images: Mapped[list['ImagesModel']] = relationship(
        'ImagesModel',
        back_populates='hotels',
        secondary='hotels_images',
    )

