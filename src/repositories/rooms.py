from models.rooms import RoomsModel
from src.repositories.base import BaseRepository


class RoomsRepository(BaseRepository):
    model = RoomsModel