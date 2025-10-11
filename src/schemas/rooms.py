from pydantic import BaseModel, field_validator

from src.schemas.facilities import Facility


class RoomAddRequest(BaseModel):
    title: str
    description: str | None = None
    price: int
    quantity: int
    facilities_ids: list[int] | None

    @field_validator("title")
    @classmethod
    def validate_not_only_digits(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("Field cannot be empty")

        # Проверяем, что строка состоит не только из цифр
        if v.isdigit():
            raise ValueError("Field cannot contain only digits")

        # Или более строгая проверка - должна быть хотя бы одна буква
        if not any(c.isalpha() for c in v):
            raise ValueError("Field must contain at least one letter")

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


class RoomBase(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None

    @field_validator("title", "description")
    @classmethod
    def not_empty(cls, v: str | None):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Поле не может быть пустым или содержать только пробелы")
        return v

    @field_validator("price", "quantity")
    @classmethod
    def positive(cls, v: int | None):
        if v is None:
            return v
        if v <= 0:
            raise ValueError("Значение должно быть больше нуля")
        return v


class RoomUpdateRequestPatch(RoomBase):
    """Для PATCH — поля опциональны"""
    pass


class RoomUpdateRequestPut(RoomBase):
    """Для PUT — поля обязательны"""
    title: str
    description: str
    price: int
    quantity: int


class RoomUpdate(BaseModel):
    hotel_id: int
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
