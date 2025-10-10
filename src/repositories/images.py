from typing import Any

from pydantic import BaseModel
from sqlalchemy import insert, Sequence, select
from src.models.images import HotelsImagesModel, ImagesModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import ImageDataMapper


class ImagesRepository(BaseRepository):
    model = ImagesModel
    mapper = ImageDataMapper


class HotelsImagesRepository(BaseRepository):
    model = HotelsImagesModel
    mapper = ImageDataMapper

    async def add_image(self, data: Sequence[BaseModel | Any]):
        add_stmt = insert(self.model).values(data).returning(self.model)
        await self.session.execute(add_stmt)

        return

    async def get_chained(self, hotel_id: int):
        select_stmt = select(self.model).where(self.model.hotel_id==hotel_id)
        result = await self.session.execute(select_stmt)

        return result.scalars().all()