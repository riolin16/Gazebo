from databases import Database
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.logger import logger

from gazebo.db.database import get_db
from gazebo.db.schemas.team_schema import TeamRead, TeamDelete, TeamCreate
from gazebo.services.team_service import TeamService

team_router = APIRouter()


@team_router.post('/', response_model=TeamRead)
async def create_team(team_create: TeamCreate, db: Database = Depends(get_db)):
    try:
        team = await TeamService.create_team(db, team_create)

        if team:
            return team

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to create team')

    except HTTPException as http_exc:
        logger.error(f'Error while creating a team: {str(http_exc)}')
        raise http_exc

    except ValueError as ve:
        logger.error(f'Error while creating a team: {str(ve)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error while creating a team: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


@team_router.delete('/{team_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_delete: TeamDelete, db: Database = Depends(get_db)):
    try:
        deleted = await TeamService.delete_team(db, team_delete)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Team not found or failed to delete')

    except HTTPException as http_exc:
        logger.error(f'Error while deleting team {team_delete.id}: {str(http_exc)}')
        raise http_exc

    except ValueError as ve:
        logger.warning(str(ve))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error deleting team {team_delete.id}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')
