from typing import Optional

from databases import Database

from gazebo.db.crud import user_crud
from gazebo.db.models.user_model import User
from gazebo.db.schemas.user_schema import UserCreate, UserRead, UserUpdate, UserDelete
from gazebo.services.auth_service import AuthService
from gazebo.services.team_service import TeamService


class UserService:
    @staticmethod
    async def create_db_user(db: Database, user_id: str, user: UserCreate) -> Optional[UserRead]:
        user_exists = await UserService.user_exists(db, user_id)
        if user_exists:
            return None

        db_user_instance = User(
            id=user_id,
            username=user.username
        )

        db_user = await user_crud.create_user(db, db_user_instance)

        if db_user:
            return UserRead(**db_user.to_dict())
        return None

    @staticmethod
    async def get_user_details_by_id(db: Database, user_id: str) -> Optional[UserRead]:
        db_user = await user_crud.read_user_by_id(db, user_id)

        if db_user:
            return UserRead(**db_user.to_dict())
        return None

    @staticmethod
    async def get_user_details_by_username(db: Database, username: str) -> Optional[UserRead]:
        db_user = await user_crud.read_user_by_username(db, username)

        if db_user:
            return UserRead(**db_user.to_dict())
        return None

    @staticmethod
    async def change_username(db: Database, user_update: UserUpdate) -> Optional[UserRead]:
        user_id = user_update.id
        username = user_update.username
        
        if not (user_id and username):
            return None
        
        user_exists = await UserService.user_exists(db, user_id)
        if not user_exists:
            return None
        
        result = await user_crud.update_username(db, user_id, username)
        if not result:
            return None

        db_user = await user_crud.read_user_by_id(db, user_id)
        if db_user:
            return UserRead(**db_user.to_dict())
        return None

    @staticmethod
    async def assign_user_to_team(db: Database, user_update: UserUpdate) -> Optional[UserRead]:
        user_id = user_update.id
        team_ids = user_update.team_id
        
        if not team_ids:
            return None

        user_exists = await UserService.user_exists(db, user_id)
        if not user_exists:
            return None

        for team_id in team_ids:
            team_exists = await TeamService.team_exists(db, team_id)
            if not team_exists:
                continue

            result = await user_crud.update_team_id(db, user_id, team_id)
            if not result:
                return None

        db_user = await user_crud.read_user_by_id(db, user_id)
        if db_user:
            return UserRead(**db_user.to_dict())
        return None

    @staticmethod
    async def delete_user(db: Database, user_delete: UserDelete) -> bool:
        user_exists = await UserService.user_exists(db, user_delete.id)
        if not user_exists:
            return False

        db_user = await user_crud.read_user_by_id(db, user_delete.id)
        deleted = await user_crud.delete_user(db, db_user)

        if deleted:
            AuthService.delete_firebase_user(user_delete.id)
            return True
        return False

    @staticmethod
    async def user_exists(db: Database, user_id: str) -> bool:
        result = await user_crud.read_user_by_id(db, user_id)
        return True if result else False
