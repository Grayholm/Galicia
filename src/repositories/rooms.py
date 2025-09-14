from sqlalchemy import delete, insert, select, update
from models.facilities import RoomsFacilitiesModel
from repositories.utils import get_rooms_ids_for_booking
from src.models.rooms import RoomsModel
from src.repositories.base import BaseRepository
from src.schemas.rooms import Room, RoomsWithRels
from sqlalchemy.orm import selectinload, joinedload

class RoomsRepository(BaseRepository):
    model = RoomsModel
    schema = Room

    async def get_rooms(self, hotel_id, filters, date_from, date_to):
        rooms_ids_to_get = get_rooms_ids_for_booking(date_from, date_to, hotel_id)

        query = (
            select(self.model)
            .where(self.model.id.in_(rooms_ids_to_get))
        )

        if filters.title:
            query = query.where(self.model.title.ilike(f"%{filters.title}%"))
        if filters.price_min is not None:
            query = query.where(self.model.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.where(self.model.price <= filters.price_max)

        query = query.options(joinedload(self.model.facilities))

        result = await self.session.execute(query)
        rooms = result.unique().scalars().all()
        return [RoomsWithRels.model_validate(room, from_attributes=True) for room in rooms]
    
    async def get_one_or_none(self, **filter):
        query = select(self.model).filter_by(**filter).options(joinedload(self.model.facilities))
        result = await self.session.execute(query)
        sth = result.unique().scalar_one_or_none()
    
        if sth:
            return RoomsWithRels.model_validate(sth, from_attributes=True)
    
        return None

    async def update(self, data, f_ids_add, f_ids_dlt, **filters):
        update_data = data.model_dump(exclude_unset=True)
        
        update_stmt = update(self.model).filter_by(**filters).values(**update_data).returning(self.model)
        result = await self.session.execute(update_stmt)

        edited = self.schema.model_validate(result.scalar_one_or_none(), from_attributes=True)
        if edited is None:
            return None

        if f_ids_dlt:
            room_id = filters.get('id')
            query = delete(RoomsFacilitiesModel).where(
                RoomsFacilitiesModel.room_id == room_id,
                RoomsFacilitiesModel.facility_id.in_(f_ids_dlt)
            )
            await self.session.execute(query)

        if not 0 in f_ids_add:
            existing_query = select(RoomsFacilitiesModel.facility_id).where(
                RoomsFacilitiesModel.room_id == room_id,
                RoomsFacilitiesModel.facility_id.in_(f_ids_add)
            )
            existing_result = await self.session.execute(existing_query)
            existing_ids = {row[0] for row in existing_result.all()}

            new_ids = [f_id for f_id in f_ids_add if f_id not in existing_ids]
            
            if new_ids:
                values_to_insert = [{
                    'room_id': room_id,
                    'facility_id': facility_id
                } for facility_id in new_ids]
                
                query = insert(RoomsFacilitiesModel).values(values_to_insert)
                await self.session.execute(query)

        return edited

