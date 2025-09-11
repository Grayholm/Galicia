
from models.facilities import FasilitiesModel
from repositories.base import BaseRepository
from schemas.fasilities import Fasilities


class FasilitiesRepository(BaseRepository):
    model = FasilitiesModel
    schema = Fasilities