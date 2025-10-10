import logging
from datetime import datetime

from sqlalchemy.exc import NoResultFound

from src.exceptions import AvailableRoomNotFoundException, RoomNotFoundException, ObjectNotFoundException, \
    InvalidDateRangeError
from src.repositories.utils import get_rooms_ids_for_booking
from src.schemas.bookings import BookingAdd
from src.services.base import BaseService


class BookingService(BaseService):
    async def get_my_bookings(self, user_id: int):
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def get_all_bookings(self):
        return await self.db.bookings.get_all()

    async def add_booking(self, data, user_id, db):
        room_data = await db.rooms.get_one_or_none(id=data.room_id)

        if room_data is None:
            raise ObjectNotFoundException

        today = datetime.now().date()

        if data.date_from >= data.date_to:
            logging.warning(f"Invalid date range: {data.date_from} to {data.date_to}")
            raise InvalidDateRangeError
        if data.date_from < today:
            return {'message': 'Дата заезда не может быть раньше сегодняшнего числа'}

        available_rooms_query = get_rooms_ids_for_booking(
            date_from=data.date_from, date_to=data.date_to
        )

        available_rooms_query = available_rooms_query.filter(
            available_rooms_query.selected_columns.room_id == data.room_id
        )

        try:
            available_room = await db.session.execute(available_rooms_query)
            available_room.scalar_one()
        except NoResultFound:
            raise AvailableRoomNotFoundException

        booking_data = BookingAdd(user_id=user_id, price=room_data.price, **data.model_dump())
        result = await db.bookings.add(booking_data)

        await self.db.commit()

        return result

    async def delete_booking(self, user_id: int, booking_id: int):
        deleted_booking = await self.db.bookings.delete(user_id=user_id, id=booking_id)
        await self.db.commit()

        return deleted_booking
