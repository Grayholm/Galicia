from pydantic import BaseModel

class Hotel(BaseModel):
    city: str
    name: str

class Update_Hotel(BaseModel):
    id: int
    city: str | None
    name: str | None