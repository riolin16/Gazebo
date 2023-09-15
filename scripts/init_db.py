import os
import re
import shutil
import subprocess

from decouple import config


def extract_env_vars(filename: str, *variables: str) -> dict:
    env_vars = {}
    with open(filename, 'r') as f:
        for line in f:
            key, value = line.strip().split('=', 1)
            if key in variables:
                env_vars[key] = value
    return env_vars


def run_sql_command(command: str):
    subprocess.run(['psql', '-U', 'postgres', '-c', command], check=True)


def main():
    # Navigate to parent directory
    os.chdir('..')

    # Set PostgreSQL's binary to PATH
    PG_PATH = config('PG_PATH')
    os.environ['PATH'] = PG_PATH + os.pathsep + os.environ['PATH']

    env_data = extract_env_vars('.env', 'ALEMBIC_DATABASE_URL', 'PGPASSWORD')
    os.environ.update(env_data)

    db_name = 'gazebo'
    sql_commands = [
        f"""
        SELECT pg_terminate_backend (pg_stat_activity.pid) 
            FROM pg_stat_activity 
            WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid();
        """,
        f"""
        DROP DATABASE IF EXISTS {db_name};
        """,
        f"""
        CREATE DATABASE {db_name} WITH
            OWNER = postgres
            ENCODING = 'UTF8'
            LC_COLLATE = 'English_United States.1252'
            LC_CTYPE = 'English_United States.1252'
            TABLESPACE = pg_default
            CONNECTION LIMIT = -1
            IS_TEMPLATE = False;
        """
    ]

    for command in sql_commands:
        run_sql_command(command)

    # Delete alembic directory and alembic.ini
    shutil.rmtree('alembic', ignore_errors=True)
    if os.path.exists('alembic.ini'):
        os.remove('alembic.ini')

    # Run alembic commands
    subprocess.run(['alembic', 'init', 'alembic'], check=True)

    # Update alembic.ini
    with open('alembic.ini', 'r') as file:
        content = file.read()
    content = re.sub(r'sqlalchemy.url = .*', 'sqlalchemy.url = ' + env_data['ALEMBIC_DATABASE_URL'], content)
    with open('alembic.ini', 'w') as file:
        file.write(content)

    # Update alembic/env.py
    os.chdir('./alembic')
    with open('env.py', 'r') as file:
        lines = file.readlines()
    with open('env.py', 'w') as file:
        for line in lines:
            if line.strip() == 'target_metadata = None':
                file.write('from gazebo.db.models import Base\n')
                file.write('target_metadata = Base.metadata\n')
            else:
                file.write(line)

    # Run alembic migrations
    os.chdir('..')
    subprocess.run(['alembic', 'revision', '--autogenerate', '-m', 'initial migration'], check=True)
    subprocess.run(['alembic', 'upgrade', 'head'], check=True)

    print('Database and migrations set up successfully.')


if __name__ == '__main__':
    main()
