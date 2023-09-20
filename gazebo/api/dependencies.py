from typing import Optional

from databases import Database
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from gazebo.db.crud.user_crud import read_user_by_id
from gazebo.db.database import get_db
from gazebo.db.models import User
from gazebo.services.auth_service import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token/')


async def get_current_user(id_token: str = Depends(oauth2_scheme), db: Database = Depends(get_db)) -> Optional[User]:
    decoded_token = AuthService.verify_firebase_token(id_token)
    if not decoded_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    user = await read_user_by_id(db, decoded_token.get('id'))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    return user
