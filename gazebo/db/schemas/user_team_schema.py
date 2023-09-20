from pydantic import BaseModel


class UserTeamBase(BaseModel):
    pass


class UserTeamCreate(UserTeamBase):
    user_id: str
    team_id: int


class UserTeamRead(UserTeamBase):
    user_id: str
    team_id: int


class UserTeamDelete(UserTeamBase):
    user_id: str
    team_id: int
