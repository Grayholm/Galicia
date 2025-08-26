from sqlalchemy import select


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def find_hotel(self, hotel_id):
        query = select(self.model).where(self.model.id == hotel_id)
        result = await self.session.execute(query)
        hotel = result.scalar_one_or_none()
    
        if hotel:
            return self.model.model_validate(hotel, from_attributes=True)
    
        return None