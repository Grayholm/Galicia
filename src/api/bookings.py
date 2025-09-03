from fastapi import APIRouter, HTTPException

from api.dependencies import DBDep
from schemas.bookings import BookingAdd, BookingAddRequest
from utils.auth_utils import UserIdDep

router = APIRouter(prefix="/bookings", tags=["Бронирования"])

@router.post("{user_id}")
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