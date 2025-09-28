from sqlalchemy.exc import NoResultFound

from src.exceptions import AvailableRoomNotFoundException
from src.repositories.utils import get_rooms_ids_for_booking
from src.schemas.bookings import BookingAdd
from src.services.base import BaseService


class BookingService(BaseService):


    async def add_booking(self, data, user_id, db):
        room_data = await db.rooms.get_one_or_none(id=data.room_id)

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

        return result