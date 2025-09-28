from src.schemas.facilities import FacilityAdd
from src.services.base import BaseService


class FacilityService(BaseService):
    async def add_facility(self, facility: FacilityAdd):
        added_facility = await self.db.facilities.add(facility)
        await self.db.commit()

        return added_facility

    async def get_facilities(self):
        return await self.db.facilities.get_all()