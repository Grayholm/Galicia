from datetime import date
from fastapi import APIRouter, HTTPException, Body, Query

from src.schemas.facilities import RoomFacilityAdd
from src.api.dependencies import DBDep, RoomsFilterDep
from src.exceptions import InvalidDateRangeError, ObjectNotFoundException, HotelNotFoundHTTPException, RoomNotFoundHTTPException
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomUpdate, RoomUpdateRequest

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms_by_filter(
    hotel_id: int,
    db: DBDep,
    filter: RoomsFilterDep,
    date_from: date = Query(examples=["2025-09-15"]),
    date_to: date = Query(examples=["2025-09-20"]),
):
    try:
        result = await db.rooms.get_rooms(hotel_id, filter, date_from, date_to)
    except InvalidDateRangeError:
        raise HTTPException(status_code=400, detail='Дата заезда позже дата выезда')
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException

    return {"Комнаты": result}


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_one_room_by_id(hotel_id: int, room_id: int, db: DBDep):
    try:
        result = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException

    return result


@router.post("/{hotel_id}/rooms")
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
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException

    room_data = RoomAdd(hotel_id=hotel_id, **data.model_dump(exclude_unset=True))
    room = await db.rooms.add(room_data)

    rooms_facilities_data = [
        RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in data.facilities_ids
    ]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()

    return {"Номер добавлен": room}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    try:
        await db.rooms.get_one(id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException

    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()

    return {"status": f"Комната {room_id} успешно удалена"}


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
    if data is None and not f_ids_to_add and not f_ids_to_dlt:
        raise HTTPException(status_code=400, detail="Отсутствуют данные для обновления")

    if (
        any(value is None for value in data.model_dump().values())
        or not f_ids_to_add
        or not f_ids_to_dlt
    ):
        raise HTTPException(status_code=400, detail="Некоторые параметры пусты")

    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    try:
        await db.rooms.get_one(id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException

    room_data = RoomUpdate(hotel_id=hotel_id, **data.model_dump())

    updated_room = await db.rooms.update(
        data=room_data,
        f_ids_add=f_ids_to_add,
        f_ids_dlt=f_ids_to_dlt,
        id=room_id,
        hotel_id=hotel_id,
    )
    await db.commit()

    if updated_room is not None:
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
    if (
        (data is None or all(value is None for value in data.model_dump().values()))
        and not f_ids_to_add
        and not f_ids_to_dlt
    ):
        raise HTTPException(status_code=400, detail="Отсутствуют данные для обновления")

    update_dict = data.model_dump(exclude_unset=True) if data else {}


    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    try:
        await db.rooms.get_one(id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException
    room_data = RoomUpdate(hotel_id=hotel_id, **update_dict)


    edited_room = await db.rooms.update(
        data=room_data,
        f_ids_add=f_ids_to_add,
        f_ids_dlt=f_ids_to_dlt,
        id=room_id,
        hotel_id=hotel_id,
    )
    await db.commit()

    if edited_room is not None:
        return {"message": f"Информация обновлена = {edited_room}"}
