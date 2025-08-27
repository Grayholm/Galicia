from repositories.hotels import HotelsRepository
from src.schemas.hotels import Hoteladd, UpdateHotel
from fastapi import Query, APIRouter, Body
from src.api.dependencies import PaginationDep
from src.db import async_session_maker
# from src.db import engine

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_hotels(
    pagination: PaginationDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Город"),   
):
    
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_hotels(title, 
                                                       location, 
                                                       pagination.per_page, 
                                                       pagination.per_page * (pagination.page-1))
    
@router.get("/{hotel_id}")
async def get_one_hotel_by_id(hotel_id: int):
    async with async_session_maker() as session:
        result = await HotelsRepository(session).find_one(hotel_id)
        if result is not None:
            return result
        
        return {"message": f"Отель с ID = {hotel_id} не найден"}


@router.post("")
async def create_hotel(hotel_data: Hoteladd = Body(openapi_examples={
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
        
    async with async_session_maker() as session:
        created_hotel = await HotelsRepository(session).add_hotels(hotel_data)
        await session.commit()

    return {"status": "Ok", "data": created_hotel}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int):  
    async with async_session_maker() as session:
        deleted_hotel = await HotelsRepository(session).delete_hotel(hotel_id)
        await session.commit()

    if deleted_hotel is None:
        return {"status": f"Hotel {hotel_id} is deleted"}
    
    return {"message": "Hotel with that ID is not found"}

@router.put("/{hotel_id}")
async def update_hotel(hotel_id: int, hotel: UpdateHotel):
    if hotel is None:
        return {"message": "Заполнены не все поля"}

    async with async_session_maker() as session:
        updated_hotel = await HotelsRepository(session).update_hotel(hotel_id, hotel)
        await session.commit()
    
    if updated_hotel is not None:
        return {"message": f"Информация обновлена = {updated_hotel}"}
    
    return {"message": "Hotel with that ID is not found"}

@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле", description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>")
async def edit_hotel(hotel_id: int, hotel: UpdateHotel | None = Body(None)):
    if hotel is None:
        return {"message": "No data to update"}
    
    async with async_session_maker() as session:
        edited_hotel = await HotelsRepository(session).edit_hotel(hotel_id, hotel)
        await session.commit()

    if edited_hotel is not None:
        return {"message": f"Информация обновлена = {edited_hotel}"}
    
    return {"message": "Hotel with that ID is not found"}