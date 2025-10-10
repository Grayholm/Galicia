from datetime import date
from fastapi import APIRouter, HTTPException, Body, Query

from src.api.dependencies import DBDep, RoomsFilterDep
from src.exceptions import (
    InvalidDateRangeError,
    ObjectNotFoundException,
    HotelNotFoundHTTPException,
    RoomNotFoundHTTPException,
    HotelNotFoundException,
    RoomNotFoundException,
    DataIsEmptyException,
    DataIntegrityError,
)
from src.schemas.rooms import RoomAddRequest, RoomUpdateRequest
from src.services.rooms import RoomService

router = APIRouter(prefix="/hotels", tags=["Панель номеров"])


@router.get(
    "/{hotel_id}/rooms",
    summary='Получить номер по фильтрам',
)
async def get_rooms_by_filter(
    hotel_id: int,
    db: DBDep,
    filters: RoomsFilterDep,
    date_from: date = Query(examples=["2025-09-15"]),
    date_to: date = Query(examples=["2025-09-20"]),
):
    try:
        result = await RoomService(db).get_rooms_by_filter(hotel_id, filters, date_from, date_to)
    except InvalidDateRangeError:
        raise HTTPException(status_code=400, detail="Дата заезда позже дата выезда")
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException

    return {"Комнаты": result}


@router.get("/{hotel_id}/rooms/{room_id}",
    summary='Получить данные номера',
    description='Получить данные одного номера по ID',
)
async def get_one_room_by_id(hotel_id: int, room_id: int, db: DBDep):
    try:
        result = await RoomService(db).get_one_room_by_id(room_id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException

    return result


@router.post("/{hotel_id}/rooms",
    summary='Добавить номер',
    description='Добавление номера к отелю',
)
async def create_room(
    hotel_id: int,
    db: DBDep,
    data: RoomAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Отель номер 1",
                "value": {
                    "title": "Русь",
                    "description": "Уютный номер из 2-ух комнат с большой кроватью",
                    "price": 6499,
                    "quantity": 2,
                    "facilities_ids": [1, 2],
                },
            }
        }
    ),
):
    try:
        room = await RoomService(db).create_room(hotel_id, data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except ValueError:
        raise HTTPException(status_code=400, detail="Название не может быть пустым")

    return {"Номер добавлен": room}


@router.put(
    "/{hotel_id}/rooms/{room_id}",
    summary="Полное обновление данных",
    description="Тут мы полностью обновляем данные, каждый параметр",
)
async def update_room(
    hotel_id: int,
    db: DBDep,
    room_id: int,
    f_ids_to_add: list[int] = Body([]),
    f_ids_to_dlt: list[int] = Body([]),
    data: RoomUpdateRequest = Body(),
):
    try:
        updated_room = await RoomService(db).update_room(
            hotel_id, room_id, f_ids_to_add, f_ids_to_dlt, data
        )
    except DataIsEmptyException:
        raise HTTPException(status_code=400, detail="Отсутствуют данные для обновления")
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException

    return {"message": f"Информация обновлена = {updated_room}"}


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частичное обновление данных об отеле",
    description="Тут мы частично обновляем данные",
)
async def partially_update_hotel(
    hotel_id: int,
    db: DBDep,
    room_id: int,
    f_ids_to_add: list[int] | None = Body([]),
    f_ids_to_dlt: list[int] | None = Body([]),
    data: RoomUpdateRequest | None = Body(),
):
    try:
        partially_updated_room = await RoomService(db).partially_update_room(
            hotel_id, room_id, f_ids_to_add, f_ids_to_dlt, data
        )
    except DataIsEmptyException:
        raise HTTPException(status_code=400, detail="Отсутствуют данные для обновления")
    except DataIntegrityError:
        raise HTTPException(status_code=400, detail="Данные значения facilities не найдены в БД")

    return {"message": f"Информация обновлена = {partially_updated_room}"}


@router.delete("/{hotel_id}/rooms/{room_id}",
    summary='Удалить номер',
)
async def delete_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        await RoomService(db).delete_room(hotel_id, room_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

    return {"status": f"Комната {room_id} успешно удалена"}
