from sqlalchemy import select
from src.repositories.mappers.mappers import UserWithHashedPasswordDataMapper
from src.repositories.base import BaseRepository
from src.models.users import UsersModel
from pydantic import EmailStr


class UsersRepository(BaseRepository):
    model = UsersModel
    mapper = UserWithHashedPasswordDataMapper

    async def get_user_with_hashed_password(self, user_email: EmailStr):
        query = select(self.model).filter_by(email=user_email)
        result = await self.session.execute(query)
        sth = result.scalar_one()

        return UserWithHashedPasswordDataMapper.map_to_domain_entity(sth)