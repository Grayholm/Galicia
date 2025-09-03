
from models.bookings import BookingsModel
from repositories.base import BaseRepository
from schemas.bookings import Booking


class BookingsRepository(BaseRepository):
    model = BookingsModel
    schema = Booking

    # async def add_booking(user_id: UserIdDep, )