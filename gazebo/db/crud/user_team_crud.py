from typing import List, Optional

from databases import Database
from fastapi.logger import logger
from sqlalchemy import select, delete

from gazebo.db.models import Team, User
from gazebo.db.models.user_team_model import UserTeam


async def create_user_in_team(db: Database, team: Team, user: User) -> Optional[UserTeam]:
    query = UserTeam.__table__.insert().values(
        user_id=user.id, team_id=team.id
    ).returning(UserTeam.user_id)

    user_id = await db.execute(query)
    if not user_id:
        return None

    db_user_team = await read_user_in_team(db, team, user)
    if not db_user_team:
        return None
    return db_user_team


async def read_users_in_team(db: Database, team: Team) -> Optional[List[User]]:
    pass


async def read_user_in_team(db: Database, team: Team, user: User) -> Optional[UserTeam]:
    query = select(UserTeam).where(UserTeam.user_id == user.id).where(UserTeam.team_id == team.id)

    result = await db.fetch_one(query)
    if result:
        return UserTeam(**dict(result))
    return None


async def delete_user_from_team(db: Database, team: Team, user: User) -> bool:
    query = delete(UserTeam).where(UserTeam.team_id == team.id).where(UserTeam.user_id == user.id)
    try:
        await db.execute(query)
        return True
    except Exception:
        return False
