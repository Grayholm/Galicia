from pydantic import BaseModel, ConfigDict


class ImageAdd(BaseModel):
    title: str
    url: str


class Image(ImageAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HotelImageAdd(BaseModel):
    hotel_id: int
    image_id: int


class HotelImage(HotelImageAdd):
    id: int
