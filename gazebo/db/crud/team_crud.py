from typing import Optional

from databases import Database
from sqlalchemy import select, delete

from gazebo.db.models import Team


async def create_team(db: Database, team: Team) -> Optional[Team]:
    query = Team.__table__.insert().values(team_name=team.team_name).returning(Team.__table__)

    result = await db.fetch_one(query)
    if result:
        return Team(**dict(result))
    return None


async def read_team_by_id(db: Database, team_id: int) -> Optional[Team]:
    query = select(Team).where(Team.id == team_id)

    result = await db.fetch_one(query)
    if result:
        return Team(**dict(result))
    return None


async def delete_team(db: Database, team: Team) -> bool:
    query = delete(Team).where(Team.id == team.id)
    try:
        await db.execute(query)
        return True
    except Exception:
        return False
