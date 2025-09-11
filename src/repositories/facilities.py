from models.facilities import RoomsFacilitiesModel, FacilitiesModel
from repositories.base import BaseRepository
from schemas.facilities import Facility, RoomFacility


class FacilitiesRepository(BaseRepository):
    model = FacilitiesModel
    schema = Facility

class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesModel
    schema = RoomFacility

    