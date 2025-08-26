from sqlalchemy import select

from src.models.hotels import HotelsModel

from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsModel

    async def get_all(self, title, location, limit, offset):
        query = select(HotelsModel)

        if title:
            query = query.where(HotelsModel.title.ilike(f"%{title}%"))
        if location:
            query = query.where(HotelsModel.location.ilike(f"%{location}%"))
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