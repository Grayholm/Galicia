from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import NoResultFound

from src.exceptions import RoomNotFoundException, InvalidDateRangeError
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
        if date_from > date_to:
            raise InvalidDateRangeError

        rooms_ids_to_get = get_rooms_ids_for_booking(date_from, date_to, hotel_id)

        query = select(self.model).where(self.model.id.in_(rooms_ids_to_get))

        if filters.title:
            query = query.where(self.model.title.ilike(f"%{filters.title}%"))
        if filters.price_min is not None:
            query = query.where(self.model.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.where(self.model.price <= filters.price_max)

        query = query.options(joinedload(self.model.facilities))
        try:
            result = await self.session.execute(query)
            rooms = result.unique().scalars().all()
        except NoResultFound:
            raise RoomNotFoundException
        return [RoomWithRelsDataMapper.map_to_domain_entity(room) for room in rooms]

    async def get_one_or_none(self, **filter):
        query = select(self.model).filter_by(**filter).options(joinedload(self.model.facilities))
        result = await self.session.execute(query)
        try:
            sth = result.unique().scalar_one()
        except NoResultFound:
            raise RoomNotFoundException

        return RoomWithRelsDataMapper.map_to_domain_entity(sth)


    async def update(self, data, f_ids_add, f_ids_dlt, **filters):
        update_data = data.model_dump(exclude_unset=True)
        room_id = filters.get("id")

        update_stmt = (
            update(self.model).filter_by(**filters).values(**update_data).returning(self.model)
        )
        try:
            result = await self.session.execute(update_stmt)
            edited = self.mapper.map_to_domain_entity(result.scalar_one_or_none())
        except NoResultFound:
            raise RoomNotFoundException

        if f_ids_dlt:
            query = delete(RoomsFacilitiesModel).where(
                RoomsFacilitiesModel.room_id == room_id,
                RoomsFacilitiesModel.facility_id.in_(f_ids_dlt),
            )
            await self.session.execute(query)

        if f_ids_add:
            valid_ids = [f_id for f_id in f_ids_add if f_id > 0]

            existing_query = select(RoomsFacilitiesModel.facility_id).where(
                RoomsFacilitiesModel.room_id == room_id,
                RoomsFacilitiesModel.facility_id.in_(valid_ids),
            )
            existing_result = await self.session.execute(existing_query)
            existing_ids = {row[0] for row in existing_result.all()}

            new_ids = [f_id for f_id in f_ids_add if f_id not in existing_ids]

            if new_ids:
                values_to_insert = [
                    {"room_id": room_id, "facility_id": facility_id} for facility_id in new_ids
                ]

                query = insert(RoomsFacilitiesModel).values(values_to_insert)
                await self.session.execute(query)

        return edited
