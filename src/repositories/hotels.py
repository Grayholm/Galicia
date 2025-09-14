from sqlalchemy import select

from repositories.mappers.mappers import HotelDataMapper
from src.models.rooms import RoomsModel
from repositories.utils import get_rooms_ids_for_booking
from src.models.hotels import HotelsModel
from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsModel
    mapper = HotelDataMapper
    
    async def get_hotels_by_time(self, title, location, limit, offset, date_from, date_to):
        rooms_ids = get_rooms_ids_for_booking(date_from, date_to)
        hotels_ids = (
            select(RoomsModel.hotel_id)
            .select_from(RoomsModel)
            .where(RoomsModel.id.in_(rooms_ids))
        )

        query = select(self.model).where(self.model.id.in_(hotels_ids))

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
        hotels = [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]
        
        return hotels