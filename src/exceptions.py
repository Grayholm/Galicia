from src.repositories.base import BaseRepository


class BaseException(Exception):
    detail = "Base Exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class RoomNotFoundException(BaseException):
    detail = "Room not found"

class AvailableRoomNotFoundException(BaseException):
    detail = "Available Room not found"