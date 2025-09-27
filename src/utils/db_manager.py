from src.repositories.bookings import BookingsRepository
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository
from src.repositories.users import UsersRepository
from src.repositories.facilities import FacilitiesRepository, RoomsFacilitiesRepository
from src.repositories.images import ImagesRepository, HotelsImagesRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

    async def __aenter__(self):
        self.session = self.session_factory

        self.hotels = HotelsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.users = UsersRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)
        self.rooms_facilities = RoomsFacilitiesRepository(self.session)
        self.images = ImagesRepository(self.session)
        self.hotels_images = HotelsImagesRepository(self.session)

        return self

    async def __aexit__(self, *args):
        if self.session is not None:
            await self.session.rollback()
            await self.session.close()

    async def commit(self):
        if self.session is not None:
            await self.session.commit()
        else:
            raise RuntimeError("Session is not initialized")
