from typing import List
from pydantic import BaseModel, Field, ConfigDict

from src.schemas.images import Image


class HotelAdd(BaseModel):
    title: str
    location: str


class HotelWithImages(HotelAdd):
    id: int
    images: List[Image]


class Hotel(HotelAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UpdateHotel(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)
