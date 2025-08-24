from schemas.schemas import Hotel, UpdateHotel
from fastapi import Query, APIRouter, Depends
from dependencies import PaginationDep

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
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return hotels

@router.post("")
async def create_hotel(hotel: Hotel):
    global hotels
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "city": hotel.city,
        "name": hotel.name
    })
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