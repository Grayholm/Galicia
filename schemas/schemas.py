from pydantic import BaseModel, Field

class Hotel(BaseModel):
    city: str
    name: str

class Update_Hotel(BaseModel):
    city: str | None = Field(None)
    name: str | None = Field(None)