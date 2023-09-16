from sqlalchemy import Column, inspect, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from gazebo.db.models import Base


class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    parent_team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)

    child_teams = relationship('Team', remote_side=[id], backref='parent_team')

    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
