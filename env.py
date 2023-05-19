#!/usr/local/bin/python3

import os

# from tools import *


dg_url: str = os.getenv("DG_URL")
dg_login: str = os.getenv('CMDB_CRED_USR')
dg_password: str = os.getenv('CMDB_CRED_PSW')

mongo_db_url: str = f"mongodb://{os.getenv('DG_MONGO_DB_CRED_USR')}:{os.getenv('DG_MONGO_DB_CRED_PSW')}@p-infra-internallb.common.novalocal:27017/cmdb?authSource=admin"
# mongo_db_url: str = f"mongodb://{os.getenv('DG_MONGO_DB_CRED_USR')}:{os.getenv('DG_MONGO_DB_CRED_PSW')}@172.26.106.3:27017/cmdb?authSource={os.getenv('DG_MONGO_DB_CRED_USR')}"

env: dict = {
    url: os.environ[url] for url in os.environ if 'PORTAL_' in url or 'OS_METRICS_' in url or 'APP_VERSIONS_' in url
}

portal_info: dict = \
    {
        url[11:]: {
            'url': env[url],
            'token': env[url.replace('URL', 'TOKEN')],
            'metrics': env['OS_METRICS_%s' % url[11:]],
            'app_versions': env['APP_VERSIONS_%s' % url[11:]]
        } for url in env if '_URL_' in url
    }
