from src.schemas.hotels import Hotel, UpdateHotel
from fastapi import Query, APIRouter, Body
from sqlalchemy import insert, select
from src.api.dependencies import PaginationDep
from src.db import async_session_maker
from src.models.hotels import HotelsModel
# from src.db import engine

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_hotels(
    pagination: PaginationDep,
    id: int | None = Query(None, description="Айдишник"),
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Город"),   
):

    async with async_session_maker() as session:
        query = select(HotelsModel)
        if id:
            query = query.where(HotelsModel.id==id)
        if title:
            query = query.where(HotelsModel.title.ilike(f"%{title}%"))
        if location:
            query = query.where(HotelsModel.location.ilike(f"%{location}%"))
        query = (
            query
            .limit(pagination.per_page)
            .offset(pagination.per_page * (pagination.page-1))
        )
        result = await session.execute(query)
        hotels = result.scalars().all()
        # print(query.compile(engine, compile_kwargs={'literal_binds': True}))  # -- Проверка SQL запроса в терминале
        # print(type(hotels), hotels)
        return hotels


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int):
    return {"status": f"hotel {hotel_id} is deleted"}

@router.post("")
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
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
        add_hotel_stmt = insert(HotelsModel).values(**hotel_data.model_dump())
        # print(add_hotel_stmt.compile(engine, compile_kwargs={'literal_binds': True}))
        await session.execute(add_hotel_stmt)
        await session.commit()

    return {"status": "Ok"}

def find_hotel(hotel_id: int):
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            return hotel
    
    return None

@router.put("/{hotel_id}")
async def update_hotel(hotel_id: int, hotel: UpdateHotel):
    hotel_ = find_hotel(hotel_id)

    if hotel_ == None:
        return {"message": "Hotel with that ID is not found"}
    
    if not hotel.city and hotel.name:
        return {"message": "Заполнены не все поля"}
    else:
        hotel_["city"] = hotel.city
        hotel_["name"] = hotel.name

    return {"message": "Информация обновлена"}

@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле", description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>")
async def edit_hotel(hotel_id: int, hotel: UpdateHotel):
    hotel_ = find_hotel(hotel_id)

    if hotel_ == None:
        return {"message": "Hotel with that ID is not found"}
    
    if not hotel.city and hotel.name:
        return {"message": "Нечего менять"}
    
    if hotel.city:
        hotel_["city"] = hotel.city
    if hotel.name:
        hotel_["name"] = hotel.name

    return {"message": "Информация обновлена"}