from typing import Optional

from pydantic import BaseModel, constr, Field


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    email: str
    password: constr(min_length=8, max_length=128)
    username: constr(min_length=3, max_length=50)


class UserRead(UserBase):
    uid: str = Field(readOnly=True)
    team_id: Optional[int] = Field(readOnly=True)


class UserUpdate(UserBase):
    uid: Optional[str]
    email: Optional[str]
    password: Optional[str]
    team_id: Optional[int]


class UserLogin(BaseModel):
    token: str


class UserAuthenticate(BaseModel):
    username: str
    password: str
