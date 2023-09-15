from databases import Database
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.logger import logger

from gazebo.api.dependencies import get_current_user
from gazebo.db.database import get_db
from gazebo.db.schemas.user_schema import UserRead
from gazebo.services.user_service import UserService

user_router = APIRouter()


@user_router.get('/me/', response_model=UserRead)
async def read_users_me(current_user: UserRead = Depends(get_current_user)):
    return current_user


@user_router.put('/{user_uid}/username/', response_model=UserRead)
async def change_username(user_uid: str, new_username: str, db: Database = Depends(get_db)):
    try:
        updated_user = await UserService.change_username(db, user_uid, new_username)

        if updated_user:
            return updated_user

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to change username')

    except ValueError as ve:
        logger.error(f'Error while updating: {str(ve)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error while updating username: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


@user_router.put('/{user_uid}/teams/{team_id}/', response_model=UserRead)
async def assign_user_to_team(user_uid: str, team_id: int, db: Database = Depends(get_db)):
    try:
        updated_user = await UserService.assign_user_to_team(db, user_uid, team_id)

        if updated_user:
            return updated_user

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to assign user to team')

    except ValueError as ve:
        logger.error(f'Error while assigning user to team: {str(ve)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error while assigning user to team: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


@user_router.delete('/{user_uid}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_uid: str, db: Database = Depends(get_db)):
    try:
        successful = await UserService.delete_user(db, user_uid)
        if not successful:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found or failed to delete')

    except ValueError as ve:
        logger.warning(str(ve))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error deleting user ID {user_uid}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')
