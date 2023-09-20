from typing import Optional, List

from pydantic import BaseModel, constr, Field


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    email: str
    password: constr(min_length=8, max_length=128)
    username: constr(min_length=3, max_length=50)


class UserRead(UserBase):
    id: str
    team_id: Optional[List[int]] = []


class UserUpdate(UserBase):
    id: str
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]


class UserDelete(BaseModel):
    id: str


class UserLogin(BaseModel):
    token: str


class UserAuthenticate(BaseModel):
    email: str
    password: str
