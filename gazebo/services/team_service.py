from databases import Database

from gazebo.db.crud import team_crud
from gazebo.db.models import Team
from gazebo.db.schemas.team_schema import TeamRead, TeamDelete, TeamCreate


class TeamService:
    @staticmethod
    async def create_team(db: Database, team_create: TeamCreate) -> TeamRead:
        db_team_instance = Team(team_name=team_create.team_name)
        team = await team_crud.create_team(db, db_team_instance)
        if team:
            return TeamRead(**team.to_dict())

    @staticmethod
    async def delete_team(db, team_delete: TeamDelete) -> bool:
        team_exists = await TeamService.team_exists(db, team_delete.id)
        if not team_exists:
            return False

        db_team = await team_crud.read_team_by_id(db, team_delete.id)
        deleted = await team_crud.delete_team(db, db_team)

        return deleted

    @staticmethod
    async def team_exists(db: Database, team_id: int) -> bool:
        result = await team_crud.read_team_by_id(db, team_id)
        return True if result else False
