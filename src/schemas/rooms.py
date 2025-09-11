from pydantic import BaseModel


class RoomAddRequest(BaseModel):
    title: str
    description: str
    price: int
    quantity: int
    facilities_ids: list[int] | None


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str
    price: int
    quantity: int


class Room(RoomAdd):
    id: int

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