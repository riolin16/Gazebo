from sqlalchemy import Column, String, inspect, Integer, ForeignKey
from sqlalchemy.orm import relationship

from gazebo.db.models import Base


class User(Base):
    __tablename__ = 'users'

    uid = Column(String(50), primary_key=True, index=True)  # also Firebase UID
    username = Column(String, unique=True, nullable=False, index=True)

    team_id = Column(Integer, ForeignKey('teams.id'), index=True)
    team = relationship('Team', backref='users')

    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
