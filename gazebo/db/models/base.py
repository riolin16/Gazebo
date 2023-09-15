from sqlalchemy.ext.declarative import declarative_base

from gazebo.db.database import metadata

Base = declarative_base(metadata=metadata)
