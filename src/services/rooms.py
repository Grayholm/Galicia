from datetime import date

from src.api.dependencies import RoomsFilterDep
from src.exceptions import ObjectNotFoundException, RoomNotFoundException, DataIsEmptyException
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAddRequest, RoomAdd, RoomUpdateRequest, RoomUpdate
from src.services.base import BaseService
from src.services.hotels import HotelService


class RoomService(BaseService):
    async def get_rooms_by_filter(
            self,
            hotel_id: int,
            filters: RoomsFilterDep,
            date_from: date,
            date_to: date,
    ):
        return await self.db.rooms.get_rooms(hotel_id, filters, date_from, date_to)

    async def get_one_room_by_id(self, room_id: int, hotel_id: int):
        return await self.db.rooms.get_one_room(id=room_id, hotel_id=hotel_id)

    async def create_room(self, hotel_id: int, data: RoomAddRequest):
        await HotelService(self.db).get_hotel_with_check(hotel_id)

        room_data = RoomAdd(hotel_id=hotel_id, **data.model_dump(exclude_unset=True))
        room = await self.db.rooms.add(room_data)

        rooms_facilities_data = [
            RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in data.facilities_ids
        ]
        await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()

        return room

    async def delete_room(self, hotel_id: int, room_id: int):
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        await self.db.rooms.delete(hotel_id=hotel_id, id=room_id)
        await self.db.commit()

    async def update_room(
            self,
            hotel_id: int,
            room_id: int,
            f_ids_to_add: list[int],
            f_ids_to_dlt: list[int],
            data: RoomUpdateRequest,
    ):
        if data is None and not f_ids_to_add and not f_ids_to_dlt:
            raise DataIsEmptyException

        if (
                any(value is None for value in data.model_dump().values())
                or not f_ids_to_add
                or not f_ids_to_dlt
        ):
            raise DataIsEmptyException

        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        room_data = RoomUpdate(hotel_id=hotel_id, **data.model_dump())

        updated_room = await self.db.rooms.update(
            data=room_data,
            f_ids_add=f_ids_to_add,
            f_ids_dlt=f_ids_to_dlt,
            id=room_id,
            hotel_id=hotel_id,
        )
        await self.db.commit()

        return updated_room

    async def partially_update_room(
            self,
            hotel_id: int,
            room_id: int,
            f_ids_to_add: list[int],
            f_ids_to_dlt: list[int],
            data: RoomUpdateRequest,
    ):
        if (
                (data is None or all(value is None for value in data.model_dump().values()))
                and not f_ids_to_add
                and not f_ids_to_dlt
        ):
            raise DataIsEmptyException

        update_dict = data.model_dump(exclude_unset=True) if data else {}

        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)
        room_data = RoomUpdate(hotel_id=hotel_id, **update_dict)

        edited_room = await self.db.rooms.update(
            data=room_data,
            f_ids_add=f_ids_to_add,
            f_ids_dlt=f_ids_to_dlt,
            id=room_id,
            hotel_id=hotel_id,
        )
        await self.db.commit()

        return edited_room

    async def get_room_with_check(self, room_id: int):
        try:
            await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException
