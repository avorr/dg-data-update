#!/usr/local/bin/python3
import os

for env_var in ("DG_URL", "DG_USR", "DG_PSW", "DG_MONGODB_HOST", "DG_MONGODB_USR", "DG_MONGODB_PSW"):
    if env_var not in os.environ:
        raise EnvironmentError(f"Failed because environment variable {env_var} is not set.")

dg_url: str = os.getenv("DG_URL")
dg_login: str = os.getenv("DG_USR")
dg_password: str = os.getenv("DG_PSW")

mongodb: str = os.getenv("DG_MONGODB_HOST")
mongodb_usr: str = os.getenv("DG_MONGODB_USR")
mongodb_psw: str = os.getenv("DG_MONGODB_PSW")

mongo_db_url: str = f'mongodb://{mongodb_usr}:{mongodb_psw}@{mongodb}?authSource=admin'

portal_info: dict = {
    'url': os.getenv("PORTAL_URL"),
    'token': os.getenv("PORTAL_TOKEN"),
    'metrics': os.getenv("K8S_METRICS"),
    'app_versions': os.getenv("APP_VERSIONS")
}
