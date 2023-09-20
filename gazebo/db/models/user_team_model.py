from sqlalchemy import Column, String, ForeignKey, Integer, inspect
from sqlalchemy.orm import relationship

from gazebo.db.models import Base


class UserTeam(Base):
    __tablename__ = 'user_team'

    user_id = Column(String(50), ForeignKey('users.id'), primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True, index=True)

    user = relationship('User', back_populates='user_team')
    team = relationship('Team', back_populates='team_users')

    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
