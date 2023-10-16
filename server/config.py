import os
import uuid

UPLOAD_DIR_ENV = 'UPLOAD_DIR'
OUTPUT_DIR_ENV = 'OUTPUT_DIR'
TMP_DIR_ENV = 'TEMP_DIR'


def ensure_dirs():
    ensure_dir(UPLOAD_DIR_ENV)
    ensure_dir(OUTPUT_DIR_ENV)
    ensure_dir(TMP_DIR_ENV)


def ensure_dir(env_name: str):
    directory = os.getenv(env_name)
    if not directory:
        directory = env_name
        os.environ[env_name] = directory

    if not os.path.exists(directory):
        os.makedirs(directory)


def get_upload_dir_path() -> str:
    return os.path.abspath(os.getenv(UPLOAD_DIR_ENV))


def get_output_dir_path() -> str:
    return os.path.abspath(os.getenv(OUTPUT_DIR_ENV))


def get_project_output_file_path(project_id: uuid):
    file_name = f'{project_id}.mp4'
    return os.path.join(get_output_dir_path(), file_name)


def get_project_status_file_path(project_id: uuid):
    file_name = f'{project_id}.txt'
    return os.path.join(get_output_dir_path(), file_name)


def get_temp_dir_path() -> str:
    return os.path.abspath(os.getenv(TMP_DIR_ENV))


def get_project_temp_dir_path(project_id: uuid) -> str:
    print("proj tmp dir path", project_id)
    return os.path.join(get_temp_dir_path(), str(project_id))
