from sqlalchemy import select, func

from models.bookings import BookingsModel
from src.models.rooms import RoomsModel
from src.repositories.base import BaseRepository
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsModel
    schema = Room

    async def get_rooms(self, hotel_id, filters):
        rooms_count = (
            select(
                BookingsModel.room_id, 
                func.count('*').label('rooms_booked')
            )
            .where(
                (BookingsModel.date_from < filters.date_to) &
                (BookingsModel.date_to > filters.date_from)
            )
            .group_by(BookingsModel.room_id)
            .cte('rooms_count')
        )

        rooms_left_table = (
            select(
                self.model.id.label('room_id'),
                (self.model.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label('rooms_left')
            )
            .select_from(self.model)
            .outerjoin(rooms_count, self.model.id == rooms_count.c.room_id)
            .cte('rooms_left_table')
        )

        rooms_ids_for_hotel = (
            select(RoomsModel.id)
            .select_from(RoomsModel)
            .filter_by(hotel_id=hotel_id)
            .subquery()
        )

        query = (
            select(self.model)
            .join(rooms_left_table, self.model.id == rooms_left_table.c.room_id)
            .where(rooms_left_table.c.rooms_left > 0, rooms_left_table.c.room_id.in_(rooms_ids_for_hotel))
        )


        if filters.title:
            query = query.where(self.model.title.ilike(f"%{filters.title}%"))
        if filters.price_min is not None:
            query = query.where(self.model.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.where(self.model.price <= filters.price_max)

        result = await self.session.execute(query)
        rooms = result.scalars().all()
        # print(query.compile(engine, compile_kwargs={'literal_binds': True}))  # -- Проверка SQL запроса в терминале
        # print(type(hotels), hotels)
        return [self.schema.model_validate(room, from_attributes=True) for room in rooms]