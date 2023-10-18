"""Module providing primary input and output configuration paths."""

import os
import uuid

UPLOAD_DIR_ENV = 'UPLOAD_DIR'
OUTPUT_DIR_ENV = 'OUTPUT_DIR'
TMP_DIR_ENV = 'TEMP_DIR'


def ensure_dirs():
    """Creates required file directories if they do not already exist."""
    ensure_dir(UPLOAD_DIR_ENV)
    ensure_dir(OUTPUT_DIR_ENV)
    ensure_dir(TMP_DIR_ENV)


def ensure_dir(env_name: str):
    """Creates directory based on env variable,
    if said directory does not already exist."""
    directory = os.getenv(env_name)
    if not directory:
        directory = env_name
        os.environ[env_name] = directory

    if not os.path.exists(directory):
        os.makedirs(directory)


def get_upload_dir_path() -> str:
    """Returns MP4 upload directory."""
    return os.path.abspath(os.getenv(UPLOAD_DIR_ENV))


def get_output_dir_path() -> str:
    """Returns final output parent directory."""
    return os.path.abspath(os.getenv(OUTPUT_DIR_ENV))


def get_project_output_file_path(project_id: uuid):
    """Returns final output file path for given project ID."""
    file_name = f'{project_id}.mp4'
    return os.path.join(get_output_dir_path(), file_name)


def get_project_status_file_path(project_id: uuid):
    """Returns status file path for given project ID."""
    file_name = f'{project_id}.txt'
    return os.path.join(get_output_dir_path(), file_name)


def get_temp_dir_path() -> str:
    """Returns parent directory path for a temporary dir, where
    clips are stored for the duration of project processing."""
    return os.path.abspath(os.getenv(TMP_DIR_ENV))


def get_project_temp_dir_path(project_id: uuid) -> str:
    """Returns project's temporary dir, where clips
    are stored for the duration of processing."""
    return os.path.join(get_temp_dir_path(), str(project_id))
