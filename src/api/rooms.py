from fastapi import APIRouter, HTTPException, Body
from src.api.dependencies import RoomsFilterDep
from src.repositories.rooms import RoomsRepository
from src.db import async_session_maker
from src.schemas.rooms import RoomAdd, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["Номера"])

@router.get("")
async def get_rooms_by_filter(filter: RoomsFilterDep):
    # if all(value is None for value in filter.model_dump().values()):
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Хотя бы один параметр фильтрации должен быть указан"
    #     )
    
    async with async_session_maker() as session:
        result = await RoomsRepository(session).get_rooms(filter)

        return {"Комнаты": result}
    

@router.get("/{room_id}")
async def get_one_room_by_id(room_id: int):
    async with async_session_maker() as session:
        result = await RoomsRepository(session).get_one_or_none(id=room_id)
        if result is not None:
            return result
        
        return {"message": f"Номер с ID = {room_id} не найден"}
    
    
@router.post("{hotel_id}")
async def create_room(data: RoomAdd = Body(openapi_examples={
    '1': {
        "summary": "Отель номер 1",
        "value": {
            "hotel_id": 13,
            "title": "Русь",
            "description": "Уютный номер из 2-ух комнат с большой кроватью",
            "price": 6499,
            "quantity": 2
        }
    }
})):
    async with async_session_maker() as session:
        result = await RoomsRepository(session).add(data)
        
        await session.commit()
    return {"Номер добавлен": result}


@router.delete("{room_id}")
async def delete_room(room_id: int):
    async with async_session_maker() as session:
        deleted_room = await RoomsRepository(session).delete(room_id)
        await session.commit()

    if deleted_room is None:
        raise HTTPException(
            status_code=404,
            detail=f"Комната с таким ID {room_id} не найдена"
        )
    
    return {"status": f"Комната {room_id} успешно удалена"}


@router.put("/{room_id}", summary="Полное обновление данных", description="Тут мы полностью обновляем данные, каждый параметр")
async def update_room(room_id: int, data: RoomUpdate):
    if data is None:
        return {"message": "Отсутствуют данные для обновления"}
    
    if any(value is None for value in data.model_dump().values()):
        raise HTTPException(
            status_code=400,
            detail="Некоторые параметры пусты"
        )

    async with async_session_maker() as session:
        updated_room = await RoomsRepository(session).update(data, room_id)
        await session.commit()
    
    if updated_room is not None:
        return {"message": f"Информация обновлена = {updated_room}"}
    
    return {"message": "Номер с таким ID не был найден"}


@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле", description="Тут мы частично обновляем данные")
async def edit_hotel(room_id: int, data: RoomUpdate | None = Body(None)):
    if data is None or all(value is None for value in data.model_dump().values()):
        raise HTTPException(
            status_code=400,
            detail="Отсутствуют данные для обновления"
        )
    
    async with async_session_maker() as session:
        edited_room = await RoomsRepository(session).update(data, room_id)
        await session.commit()

    if edited_room is not None:
        return {"message": f"Информация обновлена = {edited_room}"}
    
    return {"message": "Номер с таким ID не был найден"}