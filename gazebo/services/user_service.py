from typing import Optional

from databases import Database

from gazebo.db.crud import user_crud
from gazebo.db.models.user_model import User
from gazebo.db.schemas.user_schema import UserCreate, UserRead
from gazebo.services.auth_service import AuthService


class UserService:
    @staticmethod
    async def create_db_user(db: Database, user_uid: str, user: UserCreate) -> UserRead:
        db_user_instance = User(
            uid=user_uid,
            username=user.username,
            team_id=None
        )

        db_user = await user_crud.create_user(db, db_user_instance)

        if db_user:
            return UserRead(**db_user.to_dict())
        else:
            AuthService.delete_firebase_user(user_uid)
            raise Exception('Failed to create user in database after Firebase registration.')

    @staticmethod
    async def get_user_details_by_id(db: Database, user_uid: str) -> Optional[UserRead]:
        db_user = await user_crud.read_user_by_uid(db, user_uid)

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
    async def change_username(db: Database, user_uid: str, new_username: str) -> Optional[UserRead]:
        db_user = await user_crud.update_username(db, user_uid, new_username)

        if db_user:
            return UserRead(**db_user.to_dict())
        return None

    @staticmethod
    async def assign_user_to_team(db: Database, user_uid: str, team_id: int) -> Optional[UserRead]:
        db_user = await user_crud.update_team_id(db, user_uid, team_id)

        if db_user:
            return UserRead(**db_user.to_dict())
        return None

    @staticmethod
    async def delete_user(db: Database, user_uid: str) -> bool:
        deleted = await user_crud.delete_user(db, user_uid)

        if deleted:
            AuthService.delete_firebase_user(user_uid)
            return True
        return False
