import re

from src.exceptions import FacilityNameTooLong, FacilityAlreadyExists
from src.schemas.facilities import FacilityAdd
from src.services.base import BaseService


class FacilityService(BaseService):
    def normalize(self, text: str) -> str:
        return re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', text).lower()

    async def add_facility(self, facility: FacilityAdd):
        facility_title: str = facility.title

        if len(facility_title) > 20:
            raise FacilityNameTooLong()

        normalized_name = self.normalize(facility_title)

        existing_facilities = await self.db.facilities.get_all()
        for existing_facility in existing_facilities:
            if self.normalize(existing_facility.title) == normalized_name:
                raise FacilityAlreadyExists()
        added_facility = await self.db.facilities.add(facility)
        await self.db.commit()

        return added_facility

    async def get_facilities(self):
        return await self.db.facilities.get_all()
