from datetime import date
from src.schemas.hotels import Hoteladd, UpdateHotel
from fastapi import Query, APIRouter, Body, HTTPException
from src.api.dependencies import DBDep, PaginationDep

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Город"),
    date_from: date = Query(examples=['2025-09-15']),
    date_to: date = Query(examples=['2025-09-20'])
):
    
    return await db.hotels.get_hotels_by_time(
        title, 
        location, 
        pagination.per_page, 
        pagination.per_page * (pagination.page-1),
        date_from, 
        date_to
        )

    
@router.get("/{hotel_id}")
async def get_one_hotel_by_id(hotel_id: int, db: DBDep):
    result = await db.hotels.get_one_hotel_by_id(hotel_id)
    if result is not None:
        return result
        
    return {"message": f"Отель с ID = {hotel_id} не найден"}


@router.post("")
async def create_hotel(db: DBDep, hotel_data: Hoteladd = Body(openapi_examples={
    '1': {
        "summary": 'Отель в Дубае',
        "value": {
            'title': "Звезда",
            "location": "Дубаи"
        }
    },
    "2": {
        "summary": 'Отель в Москве',
        "value": {
            'title': "InPremium",
            "location": "Москва"
        }
    }
})):
        
    created_hotel = await db.hotels.add(hotel_data)
    await db.commit()

    return {"status": "Ok", "data": created_hotel}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep):  
    deleted_hotel = await db.hotels.delete(hotel_id)
    await db.commit()

    if deleted_hotel is None:
        return {"status": f"Hotel {hotel_id} is deleted"}
    
    return {"message": "Hotel with that ID is not found"}

@router.put("/{hotel_id}")
async def update_hotel(hotel_id: int, hotel: UpdateHotel, db: DBDep):
    if hotel.title is None or hotel.location is None:
        return {"message": "Заполнены не все поля"}

    updated_hotel = await db.hotels.update(hotel, id=hotel_id)
    await db.commit()
    
    if updated_hotel is not None:
        return {"message": f"Информация обновлена = {updated_hotel}"}
    
    return {"message": "Hotel with that ID is not found"}

@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле", description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>")
async def edit_hotel(hotel_id: int, db: DBDep, hotel: UpdateHotel | None = Body(None)):
    if hotel is None:
        return {"message": "Отсутствуют данные для обновления"}
    
    if all(value is None for value in hotel.model_dump().values()):
        raise HTTPException(
            status_code=400,
            detail="Отсутствуют данные для обновления"
        )
    
    edited_hotel = await db.hotels.update(hotel, id=hotel_id)
    await db.commit()

    if edited_hotel is not None:
        return {"message": f"Информация обновлена = {edited_hotel}"}
    
    return {"message": "Hotel with that ID is not found"}