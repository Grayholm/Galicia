import logging

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import NoResultFound

from src.exceptions import InvalidDateRangeError, ObjectNotFoundException
from src.models.facilities import RoomsFacilitiesModel
from src.repositories.mappers.mappers import RoomDataMapper, RoomWithRelsDataMapper
from src.repositories.utils import get_rooms_ids_for_booking
from src.models.rooms import RoomsModel
from src.repositories.base import BaseRepository
from sqlalchemy.orm import joinedload


class RoomsRepository(BaseRepository):
    model = RoomsModel
    mapper = RoomDataMapper

    async def get_rooms(self, hotel_id, filters, date_from, date_to):
        logging.debug(f"Getting rooms for hotel {hotel_id}, dates {date_from} to {date_to}, filters: {filters}")

        try:
            if date_from >= date_to:
                logging.warning(f"Invalid date range: {date_from} to {date_to}")
                raise InvalidDateRangeError

            rooms_ids_to_get = get_rooms_ids_for_booking(date_from, date_to, hotel_id)
            logging.debug(f"Found {len(rooms_ids_to_get)} available room IDs")

            query = select(self.model).where(self.model.id.in_(rooms_ids_to_get))

            if filters.title:
                query = query.where(self.model.title.ilike(f"%{filters.title}%"))
                logging.debug(f"Applied title filter: {filters.title}")
            if filters.price_min is not None:
                query = query.where(self.model.price >= filters.price_min)
                logging.debug(f"Applied min price filter: {filters.price_min}")
            if filters.price_max is not None:
                query = query.where(self.model.price <= filters.price_max)
                logging.debug(f"Applied max price filter: {filters.price_max}")

            query = query.options(joinedload(self.model.facilities))

            result = await self.session.execute(query)
            rooms = result.unique().scalars().all()

            if not rooms:
                logging.info(f"No rooms found for hotel {hotel_id} with given filters")
                raise ObjectNotFoundException("Rooms not found")

            logging.info(f"Found {len(rooms)} rooms for hotel {hotel_id}")
            return [RoomWithRelsDataMapper.map_to_domain_entity(room) for room in rooms]

        except InvalidDateRangeError:
            raise
        except ObjectNotFoundException:
            raise

    async def get_one_room(self, **filter):
        logging.debug(f"Getting room with filters: {filter}")

        try:
            query = select(self.model).filter_by(**filter).options(joinedload(self.model.facilities))
            result = await self.session.execute(query)

            room = result.unique().scalar_one()
            logging.debug(f"Room found with filters: {filter}")

            return RoomWithRelsDataMapper.map_to_domain_entity(room)

        except NoResultFound:
            logging.warning(f"Room not found with filters: {filter}")
            raise ObjectNotFoundException

    async def update(self, data, f_ids_add, f_ids_dlt, **filters):
        room_id = filters.get("id")
        logging.debug(f"Updating room {room_id}, add facilities: {f_ids_add}, delete facilities: {f_ids_dlt}")

        try:
            update_data = data.model_dump(exclude_unset=True)
            update_stmt = (
                update(self.model).filter_by(**filters).values(**update_data).returning(self.model)
            )

            result = await self.session.execute(update_stmt)
            edited_room = result.scalar_one()

            if not edited_room:
                logging.warning(f"Room not found for update: {filters}")
                raise ObjectNotFoundException

            edited = self.mapper.map_to_domain_entity(edited_room)
            logging.debug(f"Room {room_id} basic info updated")

            if f_ids_dlt:
                delete_query = delete(RoomsFacilitiesModel).where(
                    RoomsFacilitiesModel.room_id == room_id,
                    RoomsFacilitiesModel.facility_id.in_(f_ids_dlt),
                )
                await self.session.execute(delete_query)
                logging.debug(f"Deleted {len(f_ids_dlt)} facilities from room {room_id}")

            if f_ids_add:
                valid_ids = [f_id for f_id in f_ids_add if f_id > 0]
                logging.debug(f"Valid facility IDs to add: {valid_ids}")

                # Проверка существующих связей
                existing_query = select(RoomsFacilitiesModel.facility_id).where(
                    RoomsFacilitiesModel.room_id == room_id,
                    RoomsFacilitiesModel.facility_id.in_(valid_ids),
                )
                existing_result = await self.session.execute(existing_query)
                existing_ids = {row[0] for row in existing_result.all()}

                new_ids = [f_id for f_id in valid_ids if f_id not in existing_ids]

                if new_ids:
                    values_to_insert = [
                        {"room_id": room_id, "facility_id": facility_id} for facility_id in new_ids
                    ]
                    insert_query = insert(RoomsFacilitiesModel).values(values_to_insert)
                    await self.session.execute(insert_query)
                    logging.debug(f"Added {len(new_ids)} new facilities to room {room_id}")
                else:
                    logging.debug("No new facilities to add - all already exist")

            logging.info(f"Room {room_id} updated successfully")
            return edited

        except ObjectNotFoundException:
            raise
