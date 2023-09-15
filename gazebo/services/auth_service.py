from typing import Optional

from fastapi.logger import logger
from firebase_admin import auth
from firebase_admin.auth import ExpiredIdTokenError, RevokedIdTokenError, InvalidIdTokenError, UserRecord

from gazebo.core.config import CurrentConfig
from gazebo.db.schemas.user_schema import UserCreate, UserLogin


class AuthService:
    @staticmethod
    def register_firebase_user(user: UserCreate) -> str:
        firebase_user = auth.create_user(email=user.email, password=user.password)
        return firebase_user.uid

    @staticmethod
    def verify_firebase_token(token: str) -> Optional[dict]:
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except ExpiredIdTokenError:
            logger.warning('Firebase token has expired')
            return None
        except RevokedIdTokenError:
            logger.warning('Firebase token has been revoked')
            return None
        except InvalidIdTokenError:
            logger.warning('Firebase token is invalid')
            return None
        except Exception as e:
            logger.error(f'Unexpected error while verifying Firebase token: {str(e)}')
            return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserRecord]:
        try:
            user = auth.get_user_by_email(email)
            return user
        except Exception:
            return None

    @staticmethod
    def update_password(uid: str, new_password: str) -> Optional[bool]:
        try:
            auth.update_user(uid, password=new_password)
            return True
        except Exception as e:
            raise e

    @staticmethod
    def get_user_by_uid(uid: str) -> Optional[UserRecord]:
        try:
            user = auth.get_user(uid)
            return user
        except Exception:
            return None

    @staticmethod
    def delete_firebase_user(uid: str) -> None:
        auth.delete_user(uid)

    @staticmethod
    async def authenticate_user(user: UserLogin) -> Optional[str]:
        decoded_token = AuthService.verify_firebase_token(user.token)
        if not decoded_token:
            return None

        uid = decoded_token.get('uid')
        if not uid:
            return None
        return uid

    @staticmethod
    def _get_firebase_token(email: str, password: str):
        import requests

        api_key = CurrentConfig.FIREBASE_API_KEY
        url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}'

        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if 'idToken' in data:
            return data['idToken']
        else:
            return None
