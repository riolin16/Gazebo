Install required dependencies:
```pip install -r requirements.txt```

Using SQLAlchemy with Alembic for migrations:
1. Generate migration scripts using: ```alembic revision --autogenerate -m "describe_changes"```
2. Run migrations to create tables: ```alembic upgrade head```

Start uvicorn server by: ```uvicorn gazebo.main:app --reload```