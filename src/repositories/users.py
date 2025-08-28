from sqlalchemy import select
from src.repositories.base import BaseRepository
from src.models.users import UsersModel
from src.schemas.users import User, UserWithHashedPassword
from pydantic import EmailStr


class UsersRepository(BaseRepository):
    model = UsersModel
    schema = User

    async def get_user_with_hashed_password(self, user_email: EmailStr):
        query = select(self.model).filter_by(email=user_email)
        result = await self.session.execute(query)
        sth = result.scalar_one()

        return UserWithHashedPassword.model_validate(sth, from_attributes=True)