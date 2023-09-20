from typing import Optional, List

from pydantic import BaseModel, constr

from gazebo.db.schemas.user_schema import UserRead


class TeamBase(BaseModel):
    team_name: str


class TeamCreate(TeamBase):
    team_name: constr(min_length=3, max_length=20)


class TeamRead(TeamBase):
    id: int
    team_name: str
    users: Optional[List[UserRead]] = []


class TeamUpdate(TeamBase):
    id: Optional[List[int]]
    team_name: Optional[str]
    users: Optional[List[UserRead]]


class TeamDelete(BaseModel):
    id: int
