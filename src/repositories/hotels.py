from sqlalchemy import select, insert, update, delete

from src.models.hotels import HotelsModel
from src.schemas.hotels import Hotels, UpdateHotels
from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsModel

    async def get_hotels(self, title, location, limit, offset):
        query = select(self.model)

        if title:
            query = query.where(self.model.title.ilike(f"%{title}%"))
        if location:
            query = query.where(self.model.location.ilike(f"%{location}%"))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        hotels = result.scalars().all()
        # print(query.compile(engine, compile_kwargs={'literal_binds': True}))  # -- Проверка SQL запроса в терминале
        # print(type(hotels), hotels)
        return hotels
    
    async def add_hotels(self, hotel_data: Hotels):
        add_hotel_stmt = insert(self.model).values(**hotel_data.model_dump()).returning(self.model)
        # print(add_hotel_stmt.compile(engine, compile_kwargs={'literal_binds': True}))
        result = await self.session.execute(add_hotel_stmt)

        created_hotel = result.scalar_one()

        return created_hotel
    
    async def find_one(self, id_by):
        query = select(self.model).where(self.model.id == id_by)
        result = await self.session.execute(query)
        sth = result.scalar_one_or_none()
    
        if sth:
            return sth
    
        return None
    
    async def update_hotel(self, hotel_id, hotel: UpdateHotels):
        update_data = hotel.model_dump()
        existing_hotel = HotelsRepository(self.session).find_one(hotel_id)

        if existing_hotel is None:
            return existing_hotel
        
        update_hotel_stmt = update(HotelsModel).where(HotelsModel.id == hotel_id).values(**update_data).returning(self.model)
        await self.session.execute(update_hotel_stmt)

        return update_hotel_stmt
    
    async def edit_hotel(self, hotel_id, hotel: UpdateHotels | None):
        update_data = hotel.model_dump(exclude_unset=True)
        existing_hotel = await HotelsRepository(self.session).find_one(hotel_id)

        if existing_hotel is None:
            return existing_hotel
        
        edit_hotel_stmt = update(HotelsModel).where(HotelsModel.id == hotel_id).values(**update_data).returning(self.model)
        await self.session.execute(edit_hotel_stmt)

        return edit_hotel_stmt
    
    async def delete_hotel(self, hotel_id):
        existing_hotel = HotelsRepository(self.session).find_one(hotel_id)
        if existing_hotel is None:
            return existing_hotel
        delete_hotel_stmt = delete(HotelsModel).where(HotelsModel.id == hotel_id)
        await self.session.execute(delete_hotel_stmt)