from pydantic import BaseModel, Field, ConfigDict, EmailStr

class UserRequestAdd(BaseModel):
    first_name: str | None = Field("John")
    last_name: str | None = Field("Doe")
    nickname: str
    birth_day: int | None = Field(None)
    email: EmailStr
    phone_number: str
    password: str

class UserAdd(BaseModel):
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)
    nickname: str
    birth_day: int | None = Field(None)
    email: EmailStr
    phone_number: str
    hashed_password: str

class User(BaseModel):
    id: int
    nickname: str
    email: EmailStr
    phone_number: str