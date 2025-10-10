from pydantic import BaseModel, Field


class FacilityAdd(BaseModel):
    title: str = Field(...)


class Facility(FacilityAdd):
    id: int


class RoomFacilityAdd(BaseModel):
    room_id: int
    facility_id: int


class RoomFacility(RoomFacilityAdd):
    id: int
