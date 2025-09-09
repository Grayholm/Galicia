from repositories.utils import get_rooms_ids_for_booking
from src.models.rooms import RoomsModel
from src.repositories.base import BaseRepository
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsModel
    schema = Room

    async def get_rooms(self, hotel_id, filters, date_from, date_to):
        query = get_rooms_ids_for_booking(date_from, date_to, hotel_id)

        if filters.title:
            query = query.where(self.model.title.ilike(f"%{filters.title}%"))
        if filters.price_min is not None:
            query = query.where(self.model.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.where(self.model.price <= filters.price_max)

        result = await self.session.execute(query)
        rooms = result.scalars().all()
        return [self.schema.model_validate(room, from_attributes=True) for room in rooms]