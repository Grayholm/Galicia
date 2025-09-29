from typing import List, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

from src.schemas.images import Image


class HotelAdd(BaseModel):
    title: str
    location: str

    @field_validator('title', 'location')
    @classmethod
    def validate_not_only_digits(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError('Field cannot be empty')

        # Проверяем, что строка состоит не только из цифр
        if v.isdigit():
            raise ValueError('Field cannot contain only digits')

        # Или более строгая проверка - должна быть хотя бы одна буква
        if not any(c.isalpha() for c in v):
            raise ValueError('Field must contain at least one letter')

        return v


class HotelWithImages(HotelAdd):
    id: int
    images: List[Image]


class Hotel(HotelAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UpdateHotel(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)
