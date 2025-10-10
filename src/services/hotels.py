import re
from datetime import date


from src.api.dependencies import PaginationDep
from src.exceptions import (
    DataIsEmptyException,
    ObjectNotFoundException,
    HotelNotFoundException,
    ValidationServiceError, HotelIsAlreadyRegisteredHTTPException,
)
from src.schemas.hotels import HotelAdd, UpdateHotel
from src.services.base import BaseService
from src.services.images import ImageService


class HotelService(BaseService):
    def normalize(self, text: str) -> str:
        return re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', text).lower()

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
        hotel_title = self.normalize(hotel_data.title)
        hotel_location = self.normalize(hotel_data.location)
        existed_hotels = await self.db.hotels.get_all()
        for existed_hotel in existed_hotels:
            if self.normalize(existed_hotel.title) == hotel_title and self.normalize(existed_hotel.location) == hotel_location:
                raise HotelIsAlreadyRegisteredHTTPException
        created_hotel = await self.db.hotels.add(hotel_data)
        await self.db.commit()

        return created_hotel

    async def delete_hotel(self, hotel_id: int):
        chained_images = await self.db.hotels_images.get_chained(hotel_id)
        image_ids = [ci.image_id for ci in chained_images]
        for ci in chained_images:
            await self.db.hotels_images.delete(id=ci.id)
        deleted = await self.db.hotels.delete(id=hotel_id)

        for image_id in image_ids:
            remaining = await self.db.hotels_images.get_chained(image_id)
            if not remaining:
                image_entity = await self.db.images.get_one(id=image_id)

                try:
                    ImageService(self.db)._delete_file_from_disk(image_entity.url)
                except Exception:
                    pass

                await self.db.images.delete(id=image_id)

        await self.db.commit()

        return deleted

    async def update_hotel(self, hotel: HotelAdd, hotel_id: int):
        if hotel.title is None or hotel.location is None:
            return DataIsEmptyException("Отсутствуют данные для обновления")
        try:
            existed_hotel = await self.db.hotels.get_one_hotel_by_id(hotel_id)
        except ObjectNotFoundException:
            raise
        try:
            updated_hotel = await self.db.hotels.update(existed_hotel, id=hotel_id)
        except (ValidationServiceError, ObjectNotFoundException):
            raise

        await self.db.commit()
        return updated_hotel

    async def partially_update_item(self, hotel_id: int, hotel: UpdateHotel | None):
        if hotel is None:
            raise DataIsEmptyException("Отсутствуют данные для обновления")

        update_data = {k: v for k, v in hotel.model_dump().items() if v is not None}

        update_data = {k: v for k, v in update_data.items() if not (isinstance(v, str) and v.strip() == "")}

        if not update_data:
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
