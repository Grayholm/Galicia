from datetime import date

from sqlalchemy import select

from src.models.bookings import BookingsModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingsDataMapper


class BookingsRepository(BaseRepository):
    model = BookingsModel
    mapper = BookingsDataMapper

    async def get_bookings_with_today_checkin(self):
        query = select(self.model).filter(self.model.date_from == date.today())

        res = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

