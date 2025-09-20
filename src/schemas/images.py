from pydantic import BaseModel

class ImageAdd(BaseModel):
    title: str
    url: str

class Image(ImageAdd):
    id: int

class HotelImageAdd(BaseModel):
    hotel_id: int
    image_id: int

class HotelImage(HotelImageAdd):
    id: int