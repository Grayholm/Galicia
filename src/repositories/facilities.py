from src.repositories.mappers.mappers import FacilityDataMapper
from src.models.facilities import RoomsFacilitiesModel, FacilitiesModel
from src.repositories.base import BaseRepository
from src.schemas.facilities import RoomFacility


class FacilitiesRepository(BaseRepository):
    model = FacilitiesModel
    mapper = FacilityDataMapper


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesModel
    schema = RoomFacility
