from sqlalchemy import select, delete, update, insert
from pydantic import BaseModel

class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def find_one(self, id_by):
        query = select(self.model).where(self.model.id == id_by)
        result = await self.session.execute(query)
        sth = result.scalar_one_or_none()
    
        if sth:
            return self.schema.model_validate(sth)
    
        return None
    
    
    async def add_hotels(self, hotel_data: BaseModel):
        add_hotel_stmt = insert(self.model).values(**hotel_data.model_dump()).returning(self.model)
        # print(add_hotel_stmt.compile(engine, compile_kwargs={'literal_binds': True}))
        result = await self.session.execute(add_hotel_stmt)

        created_hotel = self.schema.model_validate(result.scalar_one_or_none())

        return created_hotel
    
    
    async def delete_hotel(self, hotel_id):
        existing_hotel = self.find_one(hotel_id)
        if existing_hotel is None:
            return existing_hotel
        delete_hotel_stmt = delete(self.model).where(self.model.id == hotel_id)
        await self.session.execute(delete_hotel_stmt)


    async def update_hotel(self, hotel_id, hotel: BaseModel):
        update_data = hotel.model_dump()
        existing_hotel = await self.find_one(hotel_id)

        if existing_hotel is None:
            return existing_hotel
        
        update_hotel_stmt = update(self.model).where(self.model.id == hotel_id).values(**update_data).returning(self.model)
        result = await self.session.execute(update_hotel_stmt)

        edited_hotel = self.schema.model_validate(result.scalar_one_or_none())

        return edited_hotel


    async def edit_hotel(self, hotel_id, hotel: BaseModel | None):
        update_data = hotel.model_dump(exclude_unset=True)
        existing_hotel = await self.find_one(hotel_id)

        if existing_hotel is None:
            return existing_hotel
        
        edit_hotel_stmt = update(self.model).where(self.model.id == hotel_id).values(**update_data).returning(self.model)
        result = await self.session.execute(edit_hotel_stmt)

        edited_hotel = self.schema.model_validate(result.scalar_one_or_none())

        return edited_hotel