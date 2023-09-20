import os
from pathlib import Path

from decouple import config


class BaseConfig:
    DEBUG = False
    TESTING = False

    SECRET_KEY = config('SECRET_KEY')
    DATABASE_URL = config('DATABASE_URL')

    BASE_DIR = Path(config('GAZEBO_ROOT', default=os.path.dirname(os.getcwd())))
    FIREBASE_CREDENTIALS_PATH = Path(config('FIREBASE_CREDENTIALS_PATH'))
    FIREBASE_API_KEY = config('FIREBASE_API_KEY')


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

CurrentConfig = configs.get(config('APP_ENV'))
