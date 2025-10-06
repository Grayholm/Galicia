from datetime import date

from sqlalchemy import select

from src.models.bookings import BookingsModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingsDataMapper


class BookingsRepository(BaseRepository):
    model = BookingsModel
    mapper = BookingsDataMapper

    def get_bookings_with_today_checkin(self):
        from datetime import date
        query = select(self.model).filter(self.model.date_from == date.today())
        res = self.session.execute(query)  # синхронный execute
        rows = res.scalars().all()
        return [self.mapper.map_to_domain_entity(booking) for booking in rows]
