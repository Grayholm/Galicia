from pydantic import BaseModel, field_validator

from src.schemas.facilities import Facility


class RoomAddRequest(BaseModel):
    title: str
    description: str | None = None
    price: int
    quantity: int
    facilities_ids: list[int] | None

    @field_validator('title')
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


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str | None = None
    price: int
    quantity: int


class Room(RoomAdd):
    id: int


class RoomsWithRels(Room):
    facilities: list[Facility]


class RoomUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None


class RoomUpdate(BaseModel):
    hotel_id: int
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
