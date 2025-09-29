import logging

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
        logging.debug(f"Searching hotels: title='{title}', location='{location}', "
                      f"dates={date_from} to {date_to}, limit={limit}, offset={offset}")

        try:
            if date_from >= date_to:
                logging.warning(f"Invalid date range: {date_from} to {date_to}")
                raise InvalidDateRangeError

            rooms_ids = get_rooms_ids_for_booking(date_from, date_to)

            hotels_ids = (
                select(RoomsModel.hotel_id).select_from(RoomsModel).where(RoomsModel.id.in_(rooms_ids))
            )

            query = select(self.model).where(self.model.id.in_(hotels_ids))

            if title:
                query = query.where(self.model.title.ilike(f"%{title}%"))
                logging.debug(f"Applied title filter: {title}")
            if location:
                query = query.where(self.model.location.ilike(f"%{location}%"))
                logging.debug(f"Applied location filter: {location}")

            query = query.limit(limit).offset(offset)
            query = query.options(joinedload(self.model.images))

            result = await self.session.execute(query)
            hotels_data = result.unique().scalars().all()

            if not hotels_data:
                logging.info(f"No hotels found for criteria: title='{title}', location='{location}'")
                raise ObjectNotFoundException("Отели не найдены")

            hotels = [
                self.mapper.map_to_domain_entity(model) for model in hotels_data
            ]

            logging.info(f"Found {len(hotels)} hotels for criteria: "
                         f"title='{title}', location='{location}', dates={date_from} to {date_to}")

            return hotels

        except InvalidDateRangeError:
            raise
        except ObjectNotFoundException:
            raise

    async def get_one_hotel_by_id(self, hotel_id: int):
        logging.debug(f"Fetching hotel by id: {hotel_id}")

        try:
            stmt = (
                select(HotelsModel)
                .options(selectinload(HotelsModel.images))
                .where(HotelsModel.id == hotel_id)
            )

            result = await self.session.execute(stmt)
            hotel = result.scalar_one()

            logging.debug(f"Successfully fetched hotel: {hotel_id}")
            return hotel

        except NoResultFound:
            logging.warning(f"Hotel not found: {hotel_id}")
            raise ObjectNotFoundException

    async def add_image(self, image: BaseModel, hotel):
        logging.debug(f"Adding image to hotel: {hotel.id}")
        image_model = ImageDataMapper.map_to_persistence_entity(image)

        hotel.images.append(image_model)

        return True

    async def add_image_to_hotel(self, hotel_id: int, image_entity: BaseModel) -> bool:
        """Добавить изображение к отелю через ORM"""
        # Получаем ORM-модель отеля
        hotel_orm = await self._get_orm_model(id=hotel_id)

        # Маппим доменную сущность в ORM-модель
        image_orm = ImageDataMapper.map_to_persistence_entity(image_entity)

        # Добавляем в коллекцию
        hotel_orm.images.append(image_orm)
        return True

    async def _get_orm_model(self, **filter_by) -> HotelsModel:
        """Получить ORM-модель вместо доменной сущности"""
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            return result.scalar_one()  # ← возвращаем ORM-модель
        except NoResultFound:
            raise ObjectNotFoundException