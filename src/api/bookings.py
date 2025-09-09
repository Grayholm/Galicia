from fastapi import APIRouter, HTTPException

from api.dependencies import DBDep
from schemas.bookings import BookingAdd, BookingAddRequest
from utils.auth_utils import UserIdDep

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
    
    booking_data = BookingAdd(user_id=user_id, price=room_data.price, **data.model_dump())
    result = await db.bookings.add(booking_data)
    await db.commit()

    return {"status": "Ok", "data": result}


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