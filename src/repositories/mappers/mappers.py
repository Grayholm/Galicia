from src.models.bookings import BookingsModel
from src.models.facilities import FacilitiesModel
from src.models.hotels import HotelsModel
from src.models.rooms import RoomsModel
from src.models.users import UsersModel
from src.models.images import HotelsImagesModel, ImagesModel
from src.repositories.mappers.base import DataMapper
from src.schemas.bookings import Booking
from src.schemas.facilities import Facility
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room, RoomsWithRels
from src.schemas.users import User, UserWithHashedPassword
from src.schemas.images import HotelImage, Image


class HotelDataMapper(DataMapper):
    db_model = HotelsModel
    schema = Hotel


class RoomDataMapper(DataMapper):
    db_model = RoomsModel
    schema = Room


class RoomWithRelsDataMapper(DataMapper):
    db_model = RoomsModel
    schema = RoomsWithRels


class BookingsDataMapper(DataMapper):
    db_model = BookingsModel
    schema = Booking


class UserDataMapper(DataMapper):
    db_model = UsersModel
    schema = User


class UserWithHashedPasswordDataMapper(DataMapper):
    db_model = UsersModel
    schema = UserWithHashedPassword


class FacilityDataMapper(DataMapper):
    db_model = FacilitiesModel
    schema = Facility


class ImageDataMapper(DataMapper):
    db_model = ImagesModel
    schema = Image


class HotelsImageDataMapper(DataMapper):
    db_model = HotelsImagesModel
    schema = HotelImage
