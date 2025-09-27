from fastapi import HTTPException


class BaseException(Exception):
    detail = "Base Exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

class DataIntegrityError(BaseException):
    detail = "Data Integrity Error"

class ObjectNotFoundException(BaseException):
    detail = "Object Not Found"

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

class DataIsEmptyException(BaseException):
    detail = "Data is empty"


class BaseHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class HotelNotFoundHTTPException(BaseHTTPException):
    status_code = 404
    detail = "Отель не найден"

class RoomNotFoundHTTPException(BaseHTTPException):
    status_code = 404
    detail = "Номер не найден"