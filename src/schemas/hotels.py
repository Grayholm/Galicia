from pydantic import BaseModel, Field, ConfigDict

class Hoteladd(BaseModel):
    title: str
    location: str

class Hotel(Hoteladd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UpdateHotel(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)