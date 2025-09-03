from pydantic import BaseModel, Field, ConfigDict


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str
    price: int
    quantity: int

class Room(RoomAdd):
    id: int

class RoomUpdate(BaseModel):
    hotel_id: int | None = Field(None)
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)