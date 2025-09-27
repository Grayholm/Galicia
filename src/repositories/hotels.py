import datetime

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.exceptions import InvalidDateRangeError, ObjectNotFoundException
from src.repositories.mappers.mappers import HotelDataMapper, ImageDataMapper
from src.models.rooms import RoomsModel
from src.repositories.utils import get_rooms_ids_for_booking
from src.models.hotels import HotelsModel
from src.repositories.base import BaseRepository
from sqlalchemy.orm import joinedload, selectinload


class HotelsRepository(BaseRepository):
    model = HotelsModel
    mapper = HotelDataMapper

    async def get_hotels_by_time(self, title, location, limit, offset, date_from, date_to):
        if date_from >= date_to:
            raise InvalidDateRangeError


        rooms_ids = get_rooms_ids_for_booking(date_from, date_to)
        hotels_ids = (
            select(RoomsModel.hotel_id).select_from(RoomsModel).where(RoomsModel.id.in_(rooms_ids))
        )

        query = select(self.model).where(self.model.id.in_(hotels_ids))

        if title:
            query = query.where(self.model.title.ilike(f"%{title}%"))
        if location:
            query = query.where(self.model.location.ilike(f"%{location}%"))

        query = query.limit(limit).offset(offset)

        query = query.options(joinedload(self.model.images))

        try:
            result = await self.session.execute(query)
            hotels_data = result.unique().scalars().all()

            if not hotels_data:
                raise ObjectNotFoundException("Отели не найдены")
            hotels = [
                self.mapper.map_to_domain_entity(model) for model in result.unique().scalars().all()
            ]
        except NoResultFound:
            raise ObjectNotFoundException

        return hotels

    async def get_one_hotel_by_id(self, hotel_id: int):
        stmt = (
            select(HotelsModel)
            .options(selectinload(HotelsModel.images))
            .where(HotelsModel.id == hotel_id)
        )
        try:
            result = await self.session.execute(stmt)
            hotel = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException

        return hotel

    async def add_image(self, image: BaseModel, hotel):
        image_model = ImageDataMapper.map_to_persistence_entity(image)

        hotel.images.append(image_model)

        return True
