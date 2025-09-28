from datetime import date

from src.schemas.bookings import BookingAdd


async def test_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAdd(
        date_from=date(year=2025, month=10, day=22),
        date_to=date(year=2025, month=10, day=30),
        room_id=room_id,
        user_id=user_id,
        price=100,
    )
    new_booking = await db.bookings.add(booking_data)
    await db.commit()

    # Получение бронирования
    assert new_booking.id is not None

    added_booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert added_booking.date_from == booking_data.date_from
    assert added_booking.date_to == booking_data.date_to
    assert added_booking.room_id == booking_data.room_id
    assert added_booking.user_id == booking_data.user_id
    assert added_booking.price == booking_data.price

    # Обновление бронирования
    update_booking_data = BookingAdd(
        date_from=date(year=2025, month=10, day=15),
        date_to=date(year=2025, month=10, day=31),
        room_id=room_id,
        user_id=user_id,
        price=1500,
    )
    updated_booking = await db.bookings.update(update_booking_data, id=new_booking.id)
    await db.commit()
    assert updated_booking.id
    assert updated_booking.price == 1500

    # Удаление бронирования
    await db.bookings.delete(id=new_booking.id)
    await db.commit()
    deleted_book = await db.bookings.get_one_or_none(id=new_booking.id)
    assert deleted_book is None
