from sqlalchemy import func, select

from src.models.bookings import BookingsModel
from src.models.rooms import RoomsModel


def get_rooms_ids_for_booking(date_from, date_to, hotel_id: int | None = None):
    rooms_count = (
        select(BookingsModel.room_id, func.count("*").label("rooms_booked"))
        .where((BookingsModel.date_from < date_to) & (BookingsModel.date_to > date_from))
        .group_by(BookingsModel.room_id)
        .cte("rooms_count")
    )

    rooms_left_table = (
        select(
            RoomsModel.id.label("room_id"),
            (RoomsModel.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label(
                "rooms_left"
            ),
            RoomsModel.hotel_id,
        )
        .outerjoin(rooms_count, RoomsModel.id == rooms_count.c.room_id)
        .cte("rooms_left_table")
    )

    query = select(rooms_left_table.c.room_id).filter(rooms_left_table.c.rooms_left > 0)

    if hotel_id:
        query = query.filter(rooms_left_table.c.hotel_id == hotel_id)

    return query
