from sqlalchemy import Column, String, inspect, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from gazebo.db.models import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)

    user_team = relationship('UserTeam', back_populates='user', cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
