import os

UPLOAD_DIR_ENV = 'UPLOAD_DIR'
OUTPUT_DIR_ENV = 'OUTPUT_DIR'
TMP_DIR_ENV = 'TEMP_DIR'


def ensure_dirs():
    ensure_dir(UPLOAD_DIR_ENV)
    ensure_dir(OUTPUT_DIR_ENV)
    ensure_dir(TMP_DIR_ENV)


def ensure_dir(env_name: str):
    dir = os.getenv(env_name)
    if not dir:
        dir = env_name
        os.environ[env_name] = dir

    if not os.path.exists(dir):
        os.makedirs(dir)


def get_upload_dir_path() -> str:
    return os.path.abspath(os.getenv(UPLOAD_DIR_ENV))


def get_output_dir_path() -> str:
    return os.path.abspath(os.getenv(OUTPUT_DIR_ENV))


def get_temp_dir_path() -> str:
    return os.path.abspath(os.getenv(TMP_DIR_ENV))
