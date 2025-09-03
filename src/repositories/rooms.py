from sqlalchemy import select

from src.models.rooms import RoomsModel
from src.repositories.base import BaseRepository
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsModel
    schema = Room

    async def get_rooms(self, filters):
        query = select(self.model)

        if filters.hotel_id:
            query = query.where(self.model.hotel_id == filters.hotel_id)
        if filters.title:
            query = query.where(self.model.title.ilike(f"%{filters.title}%"))
        if filters.price_min is not None:
            query = query.where(self.model.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.where(self.model.price <= filters.price_max)

        result = await self.session.execute(query)
        rooms = result.scalars().all()
        # print(query.compile(engine, compile_kwargs={'literal_binds': True}))  # -- Проверка SQL запроса в терминале
        # print(type(hotels), hotels)
        return [self.schema.model_validate(room, from_attributes=True) for room in rooms]