from sqlalchemy import Subquery, func, select

from models.bookings import BookingsModel
from models.rooms import RoomsModel


def get_rooms_ids_for_booking(
        date_from,
        date_to,
        hotel_id: int | None = None
    ):

    rooms_count = (
            select(
                BookingsModel.room_id, 
                func.count('*').label('rooms_booked')
            )
            .where(
                (BookingsModel.date_from < date_to) &
                (BookingsModel.date_to > date_from)
            )
            .group_by(BookingsModel.room_id)
            .cte('rooms_count')
        )

    rooms_left_table = (
        select(
            RoomsModel.id.label('room_id'),
            (RoomsModel.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label('rooms_left')
        )
        .select_from(RoomsModel)
        .outerjoin(rooms_count, RoomsModel.id == rooms_count.c.room_id)
        .cte('rooms_left_table')
    )

    rooms_ids_for_hotel = (
        select(RoomsModel.id)
        .select_from(RoomsModel)
    )
    if hotel_id:
        rooms_ids_for_hotel = rooms_ids_for_hotel.filter_by(hotel_id=hotel_id)
    
    rooms_ids_for_hotel = (
        rooms_ids_for_hotel
        .subquery()
    )

    rooms_ids_to_get = (
        select(rooms_left_table.c.room_id)
        .select_from(rooms_left_table)
        .filter(
            rooms_left_table.c.rooms_left > 0
        )
    )


    return rooms_ids_to_get