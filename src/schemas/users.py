# from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict, BaseModel, EmailStr, Field
from datetime import datetime


class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr = "@"
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: str

    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
