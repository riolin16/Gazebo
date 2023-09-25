import os
import re
import shutil
import subprocess
from pathlib import Path

PATH_DELIMITER = ';' if os.name == 'nt' else ':'
REQUIRED_VARS = ['PGPASSWORD']


def extract_env_vars(filename: Path, *variables: str) -> dict:
    env_vars = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                if not variables or key in variables:
                    env_vars[key] = value
    return env_vars


def set_env_from_file(filename: Path, *variables: str):
    env_vars = extract_env_vars(filename, *variables)

    for key, value in env_vars.items():
        if key == 'PG_PATH':
            current_path = os.environ['PATH']
            if value not in current_path:
                os.environ['PATH'] += PATH_DELIMITER + value
        elif key == 'GAZEBO_ROOT':
            current_pythonpath = os.getenv('PYTHONPATH', '')
            if value not in current_pythonpath:
                os.environ['PYTHONPATH'] = current_pythonpath + PATH_DELIMITER + value
        else:
            os.environ[key] = value

    for var in REQUIRED_VARS:
        if var not in env_vars:
            raise ValueError(f'{var} is not set.')


def run_sql_command(command: str):
    try:
        subprocess.run(['psql', '-U', 'postgres', '-c', command], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error executing SQL command: {e}')


def update_alembic_ini(alembic_ini_path: Path):
    content = alembic_ini_path.read_text()
    content = re.sub(r'sqlalchemy.url = .*', 'sqlalchemy.url = ${ALEMBIC_DATABASE_URL}', content)
    alembic_ini_path.write_text(content)


def main():
    current_path = Path.cwd()
    parent_path = current_path.parent

    if parent_path.name != 'Gazebo':
        raise Exception('Not in the Gazebo root directory.')

    env_file_path = parent_path / '.env'
    if not env_file_path.exists():
        raise FileNotFoundError(f'.env does not exist.')

    set_env_from_file(env_file_path)

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
    alembic_dir = parent_path / 'alembic'
    alembic_ini_path = parent_path / 'alembic.ini'

    if alembic_dir.exists():
        if any(alembic_dir.iterdir()):
            print('Alembic directory already exists and is not empty. Clearing it.')
            shutil.rmtree(alembic_dir)
        else:
            print('Alembic directory already exists but is empty. Deleting it.')
            alembic_dir.rmdir()

    if alembic_ini_path.exists():
        alembic_ini_path.unlink()

    # Run alembic commands
    try:
        subprocess.run(['alembic', 'init', 'alembic'], check=True, cwd=parent_path)
    except subprocess.CalledProcessError as e:
        print(f'Error initialising Alembic: {e}')
        return

    # Update alembic.ini file
    update_alembic_ini(alembic_ini_path)

    # Update alembic/env.py
    with (alembic_dir / 'env.py').open('r') as file:
        lines = file.readlines()

    with (alembic_dir / 'env.py').open('w') as file:
        for line in lines:
            if line.strip() == 'config = context.config':
                file.write(line)
                file.write('\nimport os\n')
                file.write("config.set_main_option('sqlalchemy.url', os.environ['ALEMBIC_DATABASE_URL'])\n")
            elif line.strip() == 'target_metadata = None':
                file.write('from gazebo.db.models import Base\n')
                file.write('target_metadata = Base.metadata\n')
            else:
                file.write(line)

    # Run alembic migrations
    try:
        subprocess.run(['alembic', 'revision', '--autogenerate', '-m', 'initial migration'], check=True,
                       cwd=parent_path)
        subprocess.run(['alembic', 'upgrade', 'head'], check=True, cwd=parent_path)
    except subprocess.CalledProcessError as e:
        print(f'Error running Alembic migrations: {e}')

    print('Database and migrations set up successfully.')


if __name__ == '__main__':
    main()
