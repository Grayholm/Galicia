from sqlalchemy import select


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
            return self.model.model_validate(sth, from_attributes=True)
    
        return None