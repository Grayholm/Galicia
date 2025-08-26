from src.schemas.hotels import Hotel, UpdateHotel
from fastapi import Query, APIRouter, Body
from sqlalchemy import insert, select, update, delete
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

async def find_hotel(hotel_id: int) -> Hotel:
    async with async_session_maker() as session:
        query = select(HotelsModel).where(HotelsModel.id == hotel_id)
        result = await session.execute(query)
        hotel = result.scalar_one_or_none()
    
    if hotel:
        return Hotel.model_validate(hotel, from_attributes=True)
    
    return None

@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int):
    hotel = find_hotel(hotel_id)

    if hotel is None:
        return {"message": "Hotel with that ID is not found"}
    
    async with async_session_maker() as session:
        delete_hotel_stmt = delete(HotelsModel).where(HotelsModel.id == hotel_id)
        await session.execute(delete_hotel_stmt)
        await session.commit()

    return {"status": f"hotel {hotel_id} is deleted"}

@router.put("/{hotel_id}")
async def update_hotel(hotel_id: int, hotel: UpdateHotel):
    existing_hotel = find_hotel(hotel_id)

    if existing_hotel is None:
        return {"message": "Hotel with that ID is not found"}
    
    if hotel is None:
        return {"message": "Заполнены не все поля"}
    
    update_data = hotel.model_dump()

    async with async_session_maker() as session:
        update_hotel_stmt = update(HotelsModel).where(HotelsModel.id == hotel_id).values(**update_data)
        await session.execute(update_hotel_stmt)
        await session.commit()
    
    update_hotel = find_hotel(hotel_id)

    return {"message": f"Информация обновлена = {update_hotel}"}

@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле", description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>")
async def edit_hotel(hotel_id: int, hotel: UpdateHotel | None = Body(None)):
    existing_hotel = await find_hotel(hotel_id)

    if existing_hotel is None:
        return {"message": "Hotel with that ID is not found"}
    
    if hotel is None:
        return {"message": "No data to update", "hotel": existing_hotel}
    
    update_data = hotel.model_dump(exclude_unset=True)
    
    async with async_session_maker() as session:    
        if update_data:
            edit_hotel_stmt = update(HotelsModel).where(HotelsModel.id == hotel_id).values(**update_data)
            await session.execute(edit_hotel_stmt)
            await session.commit()

    update_hotel = await find_hotel(hotel_id)

    return {"message": f"Информация обновлена = {update_hotel}"}