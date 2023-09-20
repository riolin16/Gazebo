from databases import Database
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.logger import logger
from firebase_admin import auth, exceptions

from gazebo.db.database import get_db
from gazebo.db.schemas.user_schema import UserCreate, UserRead, UserLogin, UserAuthenticate
from gazebo.services.auth_service import AuthService
from gazebo.services.user_service import UserService

auth_router = APIRouter()


@auth_router.post('/register/', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate, db: Database = Depends(get_db)):
    try:
        user_id = AuthService.register_firebase_user(user_create)
        if user_id:
            db_user: UserRead = await UserService.create_db_user(db, user_id, user_create)
            return db_user

    except exceptions.NotFoundError as e:
        logger.warning(f'Firebase error during user creation: {str(e)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered.')

    except ValueError as ve:
        logger.error(f'ValueError occurred during user creation: {str(ve)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error during user creation: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


@auth_router.post('/login/', response_model=UserRead)
async def login(user_login: UserLogin, db: Database = Depends(get_db)):
    try:
        user_id = await AuthService.authenticate_user(user_login)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Authentication failed')

        user_details = await UserService.get_user_details_by_id(db, user_id)
        if not user_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

        return user_details

    except HTTPException as http_exc:
        logger.error(f'Error while logging in: {str(http_exc)}')
        raise http_exc

    except ValueError as ve:
        logger.warning(str(ve))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f'Unexpected error during login: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')


@auth_router.post('/token/')
async def get_token(username: str = Form(...), password: str = Form(...), db: Database = Depends(get_db)):
    """
    primarily used for backend testing
    not for authentication in production
    """
    db_user = await UserService.get_user_details_by_username(db, username)

    if not db_user:
        raise HTTPException(status_code=404, detail='User not found in DB')

    firebase_user = AuthService.get_user_by_id(db_user.id)

    if not firebase_user or not hasattr(firebase_user, 'email'):
        raise HTTPException(status_code=404, detail='User not found in Firebase')

    user_auth = UserAuthenticate(**{'email': firebase_user.email, 'password': password})
    token = AuthService._get_firebase_token(user_auth)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Firebase authentication failed',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {'access_token': token, 'token_type': 'bearer'}
