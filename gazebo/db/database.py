from databases import Database
from sqlalchemy import MetaData

from gazebo.core.config import CurrentConfig

DATABASE_URL = CurrentConfig.DATABASE_URL

db = Database(DATABASE_URL)
metadata = MetaData()


async def get_db():
    await db.connect()
    try:
        yield db
    finally:
        await db.disconnect()
