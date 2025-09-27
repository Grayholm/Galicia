from pydantic import BaseModel
from sqlalchemy import insert
from src.models.images import HotelsImagesModel, ImagesModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import ImageDataMapper


class ImagesRepository(BaseRepository):
    model = ImagesModel
    mapper = ImageDataMapper
    

class HotelsImagesRepository(BaseRepository):
    model = HotelsImagesModel
    mapper = ImageDataMapper

    async def add_image(self, data: BaseModel):
        add_stmt = insert(self.model).values(data).returning(self.model)
        await self.session.execute(add_stmt)

        return