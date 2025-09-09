from datetime import date
from fastapi import APIRouter, HTTPException, Body, Query
from src.api.dependencies import DBDep, RoomsFilterDep
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomUpdate, RoomUpdateRequest

router = APIRouter(prefix="/hotels", tags=["Номера"])

@router.get("/{hotel_id}/rooms")
async def get_rooms_by_filter(
    hotel_id: int, 
    db: DBDep, 
    filter: RoomsFilterDep, 
    date_from: date = Query(), 
    date_to: date = Query()):
    result = await db.rooms.get_rooms(hotel_id, filter, date_from, date_to)

    return {"Комнаты": result}
    


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_one_room_by_id(hotel_id: int, room_id: int, db: DBDep):
    result = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    if result is not None:
        return result
        
    return {"message": f"Номер с ID = {room_id} не найден"}
    

    
@router.post("/{hotel_id}/rooms")
async def create_room(hotel_id: int, db: DBDep, data: RoomAddRequest = Body(openapi_examples={
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
    room_data = RoomAdd(hotel_id=hotel_id, **data.model_dump())
    result = await db.rooms.add(room_data)
        
    await db.commit()
    return {"Номер добавлен": result}



@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep):
    deleted_room = await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()

    if deleted_room is None:
        raise HTTPException(
            status_code=404,
            detail=f"Комната с таким ID {room_id} не найдена"
        )
    
    return {"status": f"Комната {room_id} успешно удалена"}



@router.put("/{hotel_id}/rooms/{room_id}", summary="Полное обновление данных", description="Тут мы полностью обновляем данные, каждый параметр")
async def update_room(data: RoomUpdateRequest, hotel_id: int, room_id: int, db: DBDep):
    if data is None:
        return {"message": "Отсутствуют данные для обновления"}
    
    if any(value is None for value in data.model_dump().values()):
        raise HTTPException(
            status_code=400,
            detail="Некоторые параметры пусты"
        )

    room_data = RoomUpdate(hotel_id=hotel_id, **data.model_dump())

    try:
        updated_room = await db.rooms.update(room_data, id=room_id, hotel_id=hotel_id)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Не найдена комната с заданными параметрами(Неправильное ID отеля и/или номера)")
    
    if updated_room is not None:
        return {"message": f"Информация обновлена = {updated_room}"}
    
    return {"message": "Номер с таким ID не был найден"}



@router.patch("/{hotel_id}/rooms/{room_id}", summary="Частичное обновление данных об отеле", description="Тут мы частично обновляем данные")
async def edit_hotel(hotel_id: int, db: DBDep, room_id: int, data: RoomUpdateRequest | None = Body(None)):
    if data is None or all(value is None for value in data.model_dump().values()):
        raise HTTPException(
            status_code=400,
            detail="Отсутствуют данные для обновления"
        )
    
    room_data = RoomUpdate(hotel_id=hotel_id, **data.model_dump(exclude_unset=True))

    try:
        edited_room = await db.rooms.update(room_data, id=room_id, hotel_id=hotel_id)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Не найдена комната с заданными параметрами(Неправильное ID отеля и/или номера)")

    if edited_room is not None:
        return {"message": f"Информация обновлена = {edited_room}"}
    
    return {"message": "Номер с таким ID не был найден"}