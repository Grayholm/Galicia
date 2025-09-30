from datetime import date


from src.api.dependencies import PaginationDep
from src.exceptions import DataIsEmptyException, ObjectNotFoundException, HotelNotFoundException, ValidationServiceError
from src.schemas.hotels import HotelAdd, UpdateHotel
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_hotels(
            self,
            pagination: PaginationDep,
            title: str | None,
            location: str | None,
            date_from: date,
            date_to: date,
    ):
        return await self.db.hotels.get_hotels_by_time(
            title,
            location,
            pagination.per_page,
            pagination.per_page * (pagination.page - 1),
            date_from,
            date_to,
        )


    async def get_one_hotel_by_id(self, hotel_id: int):
        return await self.db.hotels.get_one_hotel_by_id(hotel_id)

    async def create_hotel(self, hotel_data: HotelAdd):
        created_hotel = await self.db.hotels.add(hotel_data)
        await self.db.commit()

        return created_hotel

    async def delete_hotel(self, hotel_id: int):
        deleted = await self.db.hotels.delete(hotel_id)
        await self.db.commit()

        return deleted

    async def update_hotel(self, hotel: HotelAdd, hotel_id: int):
        if hotel.title is None or hotel.location is None:
            return DataIsEmptyException("Отсутствуют данные для обновления")
        try:
            updated_hotel = await self.db.hotels.update(hotel, id=hotel_id)
        except (ValidationServiceError, ObjectNotFoundException):
            raise

        await self.db.commit()
        return updated_hotel

    async def partially_update_item(self, hotel_id: int, hotel: UpdateHotel | None):
        if hotel is None:
            raise DataIsEmptyException("Отсутствуют данные для обновления")

        for k, v in hotel.model_dump().items():
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == "":
                raise DataIsEmptyException("Отсутствуют данные для обновления")

        try:
            edited_hotel = await self.db.hotels.update(hotel, id=hotel_id)
        except (ValidationServiceError, ObjectNotFoundException):
            raise

        await self.db.commit()
        return edited_hotel

    async def get_hotel_with_check(self, hotel_id: int):
        try:
            return await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException