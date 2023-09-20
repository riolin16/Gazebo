import logging
from typing import Dict

import uvicorn
from databases import Database
from fastapi import FastAPI, Request, Depends

from sqlalchemy.exc import OperationalError
from starlette.responses import JSONResponse

from gazebo.api.auth_endpoints import auth_router
from gazebo.api.team_endpoints import team_router
from gazebo.api.user_endpoints import user_router
from gazebo.core.logging import LoggingConfig
from gazebo.db.database import get_db
from gazebo.services import firebase_service

LoggingConfig.init_logging()
logger = logging.getLogger()

firebase_service.init_firebase()

app = FastAPI(docs_url='/')
app.include_router(user_router, prefix='/users', tags=['users'])
app.include_router(auth_router, prefix='/auth', tags=['authentication'])
app.include_router(team_router, prefix='/teams', tags=['teams'])


@app.exception_handler(OperationalError)
async def database_exception_handler(request: Request, exc: OperationalError):
    logger.error(f'Database error occurred during request to {request.url.path}: {exc}')
    return JSONResponse(
        status_code=503,  # Service Unavailable
        content={'message': 'Database Error', 'detail': 'Service currently unavailable. Please try again later.'},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f'Unexpected error occurred during request to {request.url.path}: {exc}')
    return JSONResponse(
        status_code=500,  # Internal Server Error
        content={'message': 'Internal Server Error', 'detail': 'An unexpected error occurred. Please try again later.'},
    )


@app.get('/health', response_model=Dict)
async def health_check(db: Database = Depends(get_db)):
    try:
        query = 'SELECT 1'
        await db.execute(query)
        return {'status': 'healthy', 'database': 'healthy'}
    except Exception as e:
        return {'status': 'unhealthy', 'database': str(e)}


@app.get('/')
def home():
    return {'Hello': 'GAZEBO'}


def main():
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
