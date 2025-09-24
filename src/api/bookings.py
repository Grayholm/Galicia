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
    return await db.bookings.add_booking(data, user_id, db)


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