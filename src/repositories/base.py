from sqlalchemy import select, delete, update, insert
from pydantic import BaseModel
from fastapi import HTTPException

from src.repositories.mappers.base import DataMapper

class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filters):
        query = select(self.model).filter(*filter).filter_by(**filters)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self):
        return await self.get_filtered()
    
    async def get_one_or_none(self, **filter):
        query = select(self.model).filter_by(**filter)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
        if sth:
            return self.mapper.map_to_domain_entity(sth)
    
        return None
    
    
    async def add(self, data: BaseModel):
        add_stmt = insert(self.model).values(**data.model_dump(exclude_unset=True)).returning(self.model)
        # print(add_hotel_stmt.compile(engine, compile_kwargs={'literal_binds': True}))
        result = await self.session.execute(add_stmt)

        created = self.mapper.map_to_domain_entity(result.scalar_one_or_none())

        return created
    
    async def add_bulk(self, data: list[BaseModel]):
        add_data_stmt = insert(self.model).values([item.model_dump(exclude_unset=True) for item in data])
        await self.session.execute(add_data_stmt)


    async def update(self, data: BaseModel, **filter):
        update_data = data.model_dump(exclude_unset=True)
        
        update_stmt = update(self.model).filter_by(**filter).values(**update_data).returning(self.model)
        result = await self.session.execute(update_stmt)

        edited = self.mapper.map_to_domain_entity(result.scalar_one_or_none())

        return edited

        
    async def delete(self, **filter):
        delete_stmt = delete(self.model).filter_by(**filter)
        result = await self.session.execute(delete_stmt)

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Object is not found")
        
        return {"message": "OK"}