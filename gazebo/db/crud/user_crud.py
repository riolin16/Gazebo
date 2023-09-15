from typing import Optional, Any, Dict

from databases import Database
from sqlalchemy import select, update, delete

from gazebo.db.models import User


async def create_user(db: Database, user: User) -> Optional[User]:
    query = User.__table__.insert().values(
        uid=user.uid,
        username=user.username,
        team_id=user.team_id
    ).returning(User.__table__)

    result = await db.fetch_one(query)
    if result:
        return User(**dict(result))
    return None


async def read_user_by_uid(db: Database, user_uid: str) -> Optional[User]:
    query = select(User).where(User.uid == user_uid)

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


async def update_user(db: Database, user_uid: str, update_data: Dict[str, Any]) -> Optional[User]:
    query = (
        update(User.__table__)
        .where(User.uid == user_uid)
        .values(**update_data)
        .returning(User.__table__)
    )
    result = await db.fetch_one(query)
    if result:
        return User(**dict(result))
    return None


async def update_username(db: Database, user_uid: str, username: str) -> Optional[User]:
    query = (
        update(User.__table__)
        .where(User.uid == user_uid)
        .values(username=username)
        .returning(User.__table__)
    )
    result = await db.fetch_one(query)
    if result:
        return User(**dict(result))
    return None


async def update_team_id(db: Database, user_uid: str, team_id: int) -> Optional[User]:
    query = (
        update(User.__table__)
        .where(User.uid == user_uid)
        .values(team_id=team_id)
        .returning(User.__table__)
    )
    result = await db.fetch_one(query)
    if result:
        return User(**dict(result))
    return None


async def delete_user(db: Database, user_uid: str) -> bool:
    query = delete(User).where(User.uid == user_uid)
    try:
        await db.execute(query)
        return True
    except Exception:
        return False
