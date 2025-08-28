from sqlalchemy import select, delete, update, insert
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, filter: dict):
        query = select(self.model).filter_by(**filter)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self):
        return await self.get_filtered()
    
    async def get_one_or_none(self, **filter):
        query = select(self.model).filter_by(**filter)
        result = await self.session.execute(query)
        sth = result.scalar_one_or_none()
    
        if sth:
            return self.schema.model_validate(sth, from_attributes=True)
    
        return None
    
    
    async def add(self, data: BaseModel):
        add_stmt = insert(self.model).values(**data.model_dump(exclude_unset=True)).returning(self.model)
        # print(add_hotel_stmt.compile(engine, compile_kwargs={'literal_binds': True}))
        result = await self.session.execute(add_stmt)

        created = self.schema.model_validate(result.scalar_one_or_none(), from_attributes=True)

        return created


    async def update(self, data: BaseModel, id):
        update_data = data.model_dump(exclude_unset=True)
        
        update_stmt = update(self.model).where(self.model.id == id).values(**update_data).returning(self.model)
        result = await self.session.execute(update_stmt)

        edited = self.schema.model_validate(result.scalar_one_or_none())

        return edited

        
    async def delete(self, id: dict):
        delete_stmt = delete(self.model).where(self.model.id == id)
        await self.session.execute(delete_stmt)