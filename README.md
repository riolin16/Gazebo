## Prerequisites
- Python 3.11 or higher
- PostgreSQL 15

## Install Dependencies
Use pip to install the required packages:
```pip install -r requirements.txt```

## Initialise Database (First-time Setup)
Navigate to the scripts directory and run the init_db.py script:
```python init_db.py```

## Database Migrations
1. Generate Migration Scripts:
  ```alembic revision --autogenerate -m "describe_changes"```
2. Run Migrations:
  ```alembic upgrade head```

## Starting the Application
Start the application using the uvicorn server. Make sure you're in the project root directory:
```uvicorn gazebo.main:app --reload```
