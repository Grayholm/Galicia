from datetime import date
import logging

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import NoResultFound

from src.exceptions import InvalidDateRangeError, ObjectNotFoundException, RoomNotFoundException
from src.models import BookingsModel
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
        logging.debug(
            f"Getting rooms for hotel {hotel_id}, dates {date_from} to {date_to}, filters: {filters}"
        )

        try:
            today = date.today()
            if date_from <= today or date_from >= date_to:
                logging.warning(f"Invalid date range: {date_from} to {date_to}")
                raise InvalidDateRangeError


            rooms_ids_to_get = get_rooms_ids_for_booking(date_from, date_to, hotel_id)
            logging.debug(f"Found {rooms_ids_to_get} available room IDs")

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
            query = (
                select(self.model).filter_by(**filter).options(joinedload(self.model.facilities))
            )
            result = await self.session.execute(query)

            room = result.unique().scalar_one()
            logging.debug(f"Room found with filters: {filter}")

            return RoomWithRelsDataMapper.map_to_domain_entity(room)

        except NoResultFound:
            logging.warning(f"Room not found with filters: {filter}")
            raise ObjectNotFoundException

    async def update(self, data, f_ids_add, f_ids_dlt, **filters):
        room_id = filters.get("id")
        logging.debug(
            f"Updating room {room_id}, add facilities: {f_ids_add}, delete facilities: {f_ids_dlt}"
        )

        try:
            update_data = {}
            if data:
                if hasattr(data, "model_dump"):
                    update_data = data.model_dump(exclude_unset=True)
                elif isinstance(data, dict):
                    update_data = data

            if update_data:
                update_stmt = (
                    update(self.model)
                    .filter_by(**filters)
                    .values(**update_data)
                    .returning(self.model)
                )
                result = await self.session.execute(update_stmt)
                edited_room = result.scalar_one_or_none()
            else:
                query = select(self.model).filter_by(**filters)
                result = await self.session.execute(query)
                edited_room = result.scalar_one_or_none()

            if not edited_room:
                logging.warning(f"Room not found for update: {filters}")
                raise ObjectNotFoundException

            edited = self.mapper.map_to_domain_entity(edited_room)
            logging.debug(f"Room {room_id} base info updated")

            if f_ids_dlt:
                delete_query = delete(RoomsFacilitiesModel).where(
                    RoomsFacilitiesModel.room_id == room_id,
                    RoomsFacilitiesModel.facility_id.in_(f_ids_dlt),
                )
                await self.session.execute(delete_query)
                logging.debug(f"Deleted {len(f_ids_dlt)} facilities from room {room_id}")

            if f_ids_add:
                existing_query = select(RoomsFacilitiesModel.facility_id).where(
                    RoomsFacilitiesModel.room_id == room_id,
                    RoomsFacilitiesModel.facility_id.in_(f_ids_add),
                )
                existing_result = await self.session.execute(existing_query)
                existing_ids = {row[0] for row in existing_result.all()}

                new_ids = [f_id for f_id in f_ids_add if f_id not in existing_ids]
                if new_ids:
                    insert_query = insert(RoomsFacilitiesModel).values(
                        [{"room_id": room_id, "facility_id": f_id} for f_id in new_ids]
                    )
                    await self.session.execute(insert_query)
                    logging.debug(f"Added {len(new_ids)} facilities to room {room_id}")
                else:
                    logging.debug("No new facilities to add")

            logging.info(f"Room {room_id} updated successfully")
            return edited

        except ObjectNotFoundException:
            raise

    async def delete_room(self, hotel_id: int, room_id: int) -> None:
        """
        Удаление комнаты с предварительным удалением связанных facilities
        """
        try:
            delete_facilities_query = delete(RoomsFacilitiesModel).where(
                RoomsFacilitiesModel.room_id == room_id
            )
            await self.session.execute(delete_facilities_query)
            logging.debug(f"Deleted facilities links for room {room_id}")

            delete_bookings_query = delete(BookingsModel).where(
                BookingsModel.room_id == room_id
            )
            await self.session.execute(delete_bookings_query)
            logging.debug(f"Deleted bookings links for room {room_id}")

            delete_room_query = delete(self.model).where(
                self.model.id == room_id, self.model.hotel_id == hotel_id
            )
            result = await self.session.execute(delete_room_query)

            if result.rowcount == 0:
                logging.warning(f"Room {room_id} in hotel {hotel_id} not found for deletion")
                raise RoomNotFoundException("Room not found")

            logging.info(f"Room {room_id} in hotel {hotel_id} deleted successfully")

        except Exception as e:
            logging.error(f"Error deleting room {room_id} from hotel {hotel_id}: {e}")
            raise
