import logging
from logging.config import dictConfig

from decouple import config

from gazebo.core.config import CurrentConfig

LOGGING_LEVELS = {
    'development': logging.DEBUG,
    'testing': logging.WARNING,
    'production': logging.INFO
}


class LoggingConfig:
    APP_ENV = config('APP_ENV', default='production')
    LOG_DIR = CurrentConfig.BASE_DIR / 'logs'
    LOG_FILE = LOG_DIR / 'gazebo_backend.log'
    LOGGING_LEVEL = LOGGING_LEVELS.get(APP_ENV, logging.WARNING)

    @classmethod
    def get_handlers(cls):
        handlers = ['file']
        if cls.APP_ENV == 'development':
            handlers.append('console')
        return handlers

    @classmethod
    def get_logging_dict_config(cls):
        log_format = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
        handlers = {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(cls.LOG_FILE),
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 10,
                'formatter': 'default',
                'level': cls.LOGGING_LEVEL,
            }
        }

        if 'console' in cls.get_handlers():
            handlers['console'] = {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': cls.LOGGING_LEVEL,
            }

        return {
            'version': 1,
            'formatters': {
                'default': {
                    'format': log_format,
                },
            },
            'handlers': handlers,
            'root': {
                'level': cls.LOGGING_LEVEL,
                'handlers': cls.get_handlers(),
            },
        }

    @classmethod
    def init_logging(cls):
        if not cls.LOG_DIR.exists():
            cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        dictConfig(cls.get_logging_dict_config())
