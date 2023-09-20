from sqlalchemy import Column, inspect, Integer, String
from sqlalchemy.orm import relationship

from gazebo.db.models import Base


class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    team_name = Column(String, unique=True, nullable=False, index=True)

    team_users = relationship('UserTeam', back_populates='team')

    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
