from typing import List
from pydantic import BaseModel, Field, ConfigDict

from src.schemas.images import Image

class Hoteladd(BaseModel):
    title: str
    location: str

class HotelWithImages(Hoteladd):
    id: int
    images: List[Image]

class Hotel(Hoteladd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UpdateHotel(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)