from typing import Optional

from databases import Database
from fastapi.logger import logger

from gazebo.db.crud import user_team_crud, team_crud, user_crud
from gazebo.db.models import Team, User, UserTeam
from gazebo.db.schemas.user_team_schema import UserTeamRead, UserTeamDelete, UserTeamCreate


class UserTeamService:
    @staticmethod
    async def add_user_to_team(db: Database, user_team_create: UserTeamCreate) -> Optional[UserTeamRead]:
        db_team = await team_crud.read_team_by_id(db, user_team_create.team_id)
        db_user = await user_crud.read_user_by_id(db, user_team_create.user_id)

        if not (db_team and db_user):
            return None

        user_in_team = await UserTeamService.is_user_in_team(db, db_team, db_user)
        if user_in_team:
            logger.info(f'User {db_user.id} already in Team {db_team.id}.')
            return None

        db_user_team = await user_team_crud.create_user_in_team(db, db_team, db_user)
        if db_user_team:
            return UserTeamRead(**db_user_team.to_dict())

        return None

    @staticmethod
    async def remove_user_from_team(db: Database, user_team_delete: UserTeamDelete) -> bool:
        db_team = await team_crud.read_team_by_id(db, user_team_delete.team_id)
        db_user = await user_crud.read_user_by_id(db, user_team_delete.user_id)

        deleted = await user_team_crud.delete_user_from_team(db, db_team, db_user)
        return deleted

    @staticmethod
    async def is_user_in_team(db: Database, db_team: Team, db_user: User) -> bool:
        if db_team and db_user:
            result = await user_team_crud.read_user_in_team(db, db_team, db_user)
            return result is not None
        return False
