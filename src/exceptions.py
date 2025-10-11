from fastapi import HTTPException


class BaseException(Exception):
    detail = "Base Exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class DataIntegrityError(BaseException):
    detail = "Data Integrity Error"


class BaseServiceError(ValueError):
    detail = "Base Service Error"


class ValidationServiceError(BaseServiceError):
    detail = "Validation error"


class ServiceUnavailableError(BaseServiceError):
    detail = "Service Unavailable"

class ImageServiceException(BaseException):
    detail = "Image Service Error"

class ImageProcessingError(BaseServiceError):
    detail = "Image Processing Error"


class ObjectNotFoundException(BaseException):
    detail = "Object Not Found"


class HotelNotFoundException(ObjectNotFoundException):
    detail = "Hotel Not Found"


class RoomNotFoundException(ObjectNotFoundException):
    detail = "Room Not Found"


class AvailableRoomNotFoundException(BaseException):
    detail = "Available Room not found"


class NicknameIsEmptyException(BaseException):
    detail = "Nickname is empty"


class EmailIsAlreadyRegisteredException(BaseException):
    detail = "Email is already registered"


class RegisterErrorException(BaseException):
    detail = "Register error"


class LoginErrorException(BaseException):
    detail = "Login error"


class InvalidDateRangeError(ValidationServiceError):
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

class HotelNotFoundForDateHTTPException(BaseHTTPException):
    status_code = 404
    detail = 'К сожалению для такой даты мы не смогли найти подходящий отель со свободными номерами'

class HotelIsAlreadyRegisteredHTTPException(BaseHTTPException):
    status_code = 409
    detail = 'Такой отель уже занесен в базу'

class RoomNotFoundHTTPException(BaseHTTPException):
    status_code = 404
    detail = "Номер не найден"

class FacilityAlreadyExists(BaseHTTPException):
    status_code = 409
    detail = "Такое удобство уже существует"

class FacilityNameTooLong(BaseHTTPException):
    status_code = 400
    detail = "Название удобства должно быть не длиннее 20 символов"

class FacilityNotFoundError(BaseException):
    def __init__(self, facility_id: int):
        self.facility_id = facility_id
        super().__init__(f"Facility with id {facility_id} not found")