from pydantic import BaseModel, Field, EmailStr

class UserRequestAddRegister(BaseModel):
    first_name: str | None = Field("John")
    last_name: str | None = Field("Doe")
    nickname: str
    birth_day: int | None = Field(None)
    email: EmailStr
    password: str

class UserAdd(BaseModel):
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)
    nickname: str
    birth_day: int | None = Field(None)
    email: EmailStr
    hashed_password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    first_name: str
    last_name: str
    birth_day: int
    id: int
    nickname: str
    email: EmailStr

class UserWithHashedPassword(User):
    hashed_password: str