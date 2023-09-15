import firebase_admin
from firebase_admin import credentials

from gazebo.core.config import CurrentConfig


def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(CurrentConfig.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
