from fastapi import APIRouter, HTTPException

from src.api.dependencies import DBDep
from src.repositories.utils import get_rooms_ids_for_booking
from src.schemas.bookings import BookingAdd, BookingAddRequest
from src.utils.auth_utils import UserIdDep

router = APIRouter(prefix="/bookings", tags=["Бронирования"])

@router.get("{user_id}")
async def get_my_bookings(
    user_id: UserIdDep,
    db: DBDep,
):
    bookings_data = await db.bookings.get_filtered(user_id=user_id)

    if not bookings_data:
        return {"message": "У вас нет бронирований"}
    
    return bookings_data


@router.get("")
async def get_all_bookings(
    db: DBDep,
):
    bookings_data = await db.bookings.get_all()
    
    return bookings_data


@router.post("")
async def add_booking(
    user_id: UserIdDep, 
    db: DBDep, 
    data: BookingAddRequest
):  
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
    await db.commit()

    return {"status": "OK", "data": result}


@router.delete("{booking_id}")
async def delete_booking(
    user_id: UserIdDep, 
    db: DBDep, 
    booking_id: int
):  
    deleted_booking = await db.bookings.delete(user_id=user_id, id=booking_id)
    await db.commit()

    if deleted_booking is None:
        raise HTTPException(
            status_code=404,
            detail=f"Бронирование с таким ID {booking_id} не найден"
        )
    
    return {"status": f"Бронирование {booking_id} успешно удалено"}