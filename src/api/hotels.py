from datetime import date


from src.exceptions import (
    InvalidDateRangeError,
    ObjectNotFoundException,
    HotelNotFoundHTTPException,
    DataIsEmptyException,
    ValidationServiceError,
)
from src.schemas.hotels import HotelAdd, UpdateHotel
from fastapi import Query, APIRouter, Body, HTTPException
from src.api.dependencies import DBDep, PaginationDep
from src.services.hotels import HotelService

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Город"),
    date_from: date = Query(examples=["2025-09-15"]),
    date_to: date = Query(examples=["2025-09-20"]),
):
    try:
        result = await HotelService(db).get_hotels(pagination, title, location, date_from, date_to)
    except InvalidDateRangeError:
        raise HTTPException(status_code=400, detail="Дата заезда позже дата выезда")
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException

    return result


@router.get("/{hotel_id}")
async def get_one_hotel_by_id(hotel_id: int, db: DBDep):
    try:
        return await HotelService(db).get_one_hotel_by_id(hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException


@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {"summary": "Отель в Дубае", "value": {"title": "Звезда", "location": "Дубаи"}},
            "2": {
                "summary": "Отель в Москве",
                "value": {"title": "InPremium", "location": "Москва"},
            },
        }
    ),
):
    created_hotel = await HotelService(db).create_hotel(hotel_data)

    return {"status": "Ok", "data": created_hotel}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep):
    deleted_hotel = await HotelService(db).delete_hotel(hotel_id)

    if deleted_hotel is None:
        return {"status": f"Hotel {hotel_id} is deleted"}

    return {"message": "Hotel with that ID is not found"}


@router.put("/{hotel_id}")
async def update_hotel(hotel_id: int, hotel: HotelAdd, db: DBDep):
    try:
        updated_hotel = await HotelService(db).update_hotel(hotel, hotel_id=hotel_id)
    except DataIsEmptyException:
        raise HTTPException(status_code=400, detail="Отсутствуют данные для обновления")
    except ValidationServiceError:
        raise HTTPException(
            status_code=400, detail="Поля не должны быть пустыми и должны быть строкой"
        )
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    if updated_hotel is not None:
        return {"message": f"Информация обновлена = {updated_hotel}"}


@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>",
)
async def partially_update_item(hotel_id: int, db: DBDep, hotel: UpdateHotel | None = Body(None)):
    try:
        edited_hotel = await HotelService(db).partially_update_item(hotel_id=hotel_id, hotel=hotel)
    except DataIsEmptyException:
        raise HTTPException(status_code=400, detail="Отсутствуют данные для обновления")
    except ValidationServiceError:
        raise HTTPException(
            status_code=400, detail="Поля не должны быть пустыми и должны быть строкой"
        )
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    if edited_hotel is not None:
        return {"message": f"Информация обновлена = {edited_hotel}"}
