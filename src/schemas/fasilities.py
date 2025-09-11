from pydantic import BaseModel

class Fasilities(BaseModel):
    title: str


class RoomsFasilitiesAdd(BaseModel):
    rooms_id: int
    fasilities_id: int