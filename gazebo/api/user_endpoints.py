from databases import Database
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.logger import logger

from gazebo.api.dependencies import get_current_user
from gazebo.db.database import get_db
from gazebo.db.schemas.user_schema import UserRead, UserUpdate, UserDelete
from gazebo.db.schemas.user_team_schema import UserTeamRead, UserTeamCreate
from gazebo.services.user_service import UserService
from gazebo.services.user_team_service import UserTeamService

user_router = APIRouter()


@user_router.get('/me/', response_model=UserRead)
async def read_users_me(current_user: UserRead = Depends(get_current_user)):
    return current_user


@user_router.put('/{user_id}/username/', response_model=UserRead)
async def change_username(
        user_id: str,
        user_update: UserUpdate,
        db: Database = Depends(get_db),
        current_user: UserRead = Depends(get_current_user)
):
    # TODO: FIXME
    try:
        if user_id != current_user.id:
            raise

        user_update.id = current_user.id
        updated_user = await UserService.change_username(db, user_update)

        if updated_user:
            return updated_user

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to change username')

    except ValueError as ve:
        logger.error(f'Error while updating: {str(ve)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error while updating username: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


@user_router.put('/{user_id}/teams/{team_id}/', response_model=UserTeamRead)
async def assign_user_to_team(user_team_create: UserTeamCreate, db: Database = Depends(get_db)):
    try:
        added_user_team = await UserTeamService.add_user_to_team(db, user_team_create)

        if added_user_team:
            return added_user_team

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to assign user to team')

    except ValueError as ve:
        logger.error(f'Error while assigning user to team: {str(ve)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error while assigning user to team: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


@user_router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_delete: UserDelete,
        db: Database = Depends(get_db),
        current_user: UserRead = Depends(get_current_user)
):
    try:
        deleted = await UserService.delete_user(db, user_delete)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found or failed to delete')

    except ValueError as ve:
        logger.warning(str(ve))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error deleting user ID {user_delete.id}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')
