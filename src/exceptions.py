

class BaseException(Exception):
    detail = "Base Exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

class DataIntegrityError(BaseException):
    detail = "Data Integrity Error"

class ObjectNotFoundException(BaseException):
    detail = "Object Not Found"

class RoomNotFoundException(BaseException):
    detail = "Room not found"

class AvailableRoomNotFoundException(BaseException):
    detail = "Available Room not found"

class NicknameIsEmptyException(BaseException):
    detail = "Nickname is empty"

class EmailIsAlreadyRegisteredException(BaseException):
    detail = "Email is already registered"

class RegisterErrorException(BaseException):
    detail = "Register error"

class InvalidDateRangeError(BaseException):
    detail = "Invalid date range"

class HotelNotFoundException(BaseException):
    detail = "Hotel not found"

class DataIsEmptyException(BaseException):
    detail = "Data is empty"