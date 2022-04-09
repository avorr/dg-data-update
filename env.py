#!/usr/bin/python3

import os
import json

from tools import *

# cf_login: str = os.environ['CF_LOGIN']
# cf_password: str = os.environ['CF_PASS']

cmdb_login: str = os.environ['CMDB_CRED_USR']
cmdb_password: str = os.environ['CMDB_CRED_PSW']

mongo_db_login: str = 'admin'
mongo_db_pass: str = 'nk63QXkzCW'

mongo_db_url: str = 'mongodb://%s:%s@p-infra-internallb.common.novalocal:27017/cmdb?authSource=admin' % \
                    (os.environ['DG_MONGO_DB_CRED_USR'], os.environ['DG_MONGO_DB_CRED_PSW'])

env: dict = \
    {
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
