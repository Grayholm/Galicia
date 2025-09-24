from datetime import date

from fastapi import HTTPException
from sqlalchemy import select

from src.models.bookings import BookingsModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingsDataMapper
from src.repositories.utils import get_rooms_ids_for_booking
from src.schemas.bookings import BookingAdd


class BookingsRepository(BaseRepository):
    model = BookingsModel
    mapper = BookingsDataMapper

    async def get_bookings_with_today_checkin(self):
        query = (
            select(self.model)
            .filter(self.model.date_from == date.today())
        )

        res = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def add_booking(self, data, user_id, db):
        room_data = await db.rooms.get_one_or_none(id=data.room_id)

        if not room_data:
            raise HTTPException(status_code=404, detail="Номер не найден")

        available_rooms_query = get_rooms_ids_for_booking(
            date_from=data.date_from,
            date_to=data.date_to
        )

        available_rooms_query = available_rooms_query.filter(
            available_rooms_query.selected_columns.room_id == data.room_id
        )

        available_room = await db.session.execute(available_rooms_query)
        available_room = available_room.scalar_one_or_none()

        if not available_room:
            raise HTTPException(
                status_code=400,
                detail="На выбранные даты все номера этого типа заняты"
            )

        booking_data = BookingAdd(user_id=user_id, price=room_data.price, **data.model_dump())
        result = await db.bookings.add(booking_data)

        return result