from src.models.bookings import BookingsModel
from src.models.facilities import FacilitiesModel
from src.models.hotels import HotelsModel
from src.models.rooms import RoomsModel
from src.models.users import UsersModel
from repositories.mappers.base import DataMapper
from schemas.bookings import Booking
from schemas.facilities import Facility
from schemas.hotels import Hotel
from schemas.rooms import Room, RoomsWithRels
from schemas.users import User, UserWithHashedPassword


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