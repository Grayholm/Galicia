
from src.models.bookings import BookingsModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingsDataMapper


class BookingsRepository(BaseRepository):
    model = BookingsModel
    mapper = BookingsDataMapper