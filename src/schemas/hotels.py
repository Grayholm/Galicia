from pydantic import BaseModel, Field

class Hotels(BaseModel):
    title: str
    location: str

class UpdateHotels(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)