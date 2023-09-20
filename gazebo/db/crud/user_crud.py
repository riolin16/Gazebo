from typing import Optional

from databases import Database
from sqlalchemy import select, update, delete

from gazebo.db.models import User
from gazebo.db.models.user_team_model import UserTeam


async def create_user(db: Database, user: User) -> Optional[User]:
    query = User.__table__.insert().values(
        id=user.id,
        username=user.username
    ).returning(User.__table__)

    result = await db.fetch_one(query)
    if result:
        return User(**dict(result))
    return None


async def read_user_by_id(db: Database, user_id: str) -> Optional[User]:
    query = select(User).where(User.id == user_id)

    result = await db.fetch_one(query)
    if result:
        return User(**dict(result))
    return None


async def read_user_by_username(db: Database, username: str) -> Optional[User]:
    query = select(User).where(User.username == username)

    result = await db.fetch_one(query)
    if result:
        return User(**dict(result))
    return None


async def update_username(db: Database, user_id: str, new_username: str) -> bool:
    query = (
        update(User.__table__).where(User.id == user_id).values(username=new_username)
    )
    result = await db.fetch_one(query)
    if not result:
        return False
    return True


async def update_team_id(db: Database, user_id: str, new_team_id: int) -> bool:
    query = (
        UserTeam.__table__.insert().values(user_id=user_id, team_id=new_team_id)
    )
    result = await db.execute(query)
    return result is not None


async def delete_user(db: Database, user: User) -> bool:
    query = delete(User).where(User.id == user.id)
    try:
        await db.execute(query)
        return True
    except Exception:
        return False
