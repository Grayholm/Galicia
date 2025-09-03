from sqlalchemy import select

from src.models.hotels import HotelsModel
from src.schemas.hotels import Hotel
from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsModel
    schema = Hotel

    async def get_hotels(self, title, location, limit, offset):
        query = select(self.model)

        if title:
            query = query.where(self.model.title.ilike(f"%{title}%"))
        if location:
            query = query.where(self.model.location.ilike(f"%{location}%"))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        hotels = result.scalars().all()
        # print(query.compile(engine, compile_kwargs={'literal_binds': True}))  # -- Проверка SQL запроса в терминале
        # print(type(hotels), hotels)
        return hotels