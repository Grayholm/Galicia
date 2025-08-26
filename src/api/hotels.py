from src.schemas.hotels import Hotel, UpdateHotel
from fastapi import Query, APIRouter, Body
from sqlalchemy import insert
from src.api.dependencies import PaginationDep
from src.db import async_session_maker
from src.models.hotels import HotelsModel
# from src.db import engine

router = APIRouter(prefix="/hotels", tags=["Отели"])

hotels = [
    {"id": 1, "city": "Сочи", "name": "sochi"},
    {"id": 2, "city": "Дубаи", "name": "dubai"},
    {"id": 3, "city": "Мальдивы", "name": "maldivi"},
    {"id": 4, "city": "Геленджик", "name": "gelendzhik"},
    {"id": 5, "city": "Москва", "name": "moscow"},
    {"id": 6, "city": "Казань", "name": "kazan"},
    {"id": 7, "city": "Санкт-Петербург", "name": "spb"}
]

@router.get("")
async def get_hotels(
    pagination: PaginationDep,
    id: int | None = Query(None, description="Айдишник"),
    city: str | None = Query(None, description="Город"),
    name: str | None = Query(None, description="Название отеля на английском"),   
):
    
    hotels_ = []

    if id or city or name:
        for hotel in hotels:
            if id and hotel["id"] != id:
                continue
            if city and hotel["city"] != city:
                continue
            if name and hotel["name"] != name:
                continue
            hotels_.append(hotel)
        return hotels_[pagination.per_page * (pagination.page-1):][:pagination.per_page]

    if not id and not city and not name:
        return hotels[pagination.per_page * (pagination.page-1):][:pagination.per_page]


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