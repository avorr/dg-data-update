#!/usr/bin/python3

import os
import json

from creds import *
def jsonRead(json_object: dict):
    print(json.dumps(json_object, indent=4))

cmdb_login: str = os.environ['CMDB_CRED_USR']
cmdb_password: str = os.environ['CMDB_CRED_PSW']

env: dict = \
    {url: os.environ[url] for url in os.environ if 'PORTAL_' in url or 'OS_METRICS_' in url or 'PPRB3_VERSIONS_' in url}

portal_info: dict = \
    {url[11:]: {'url': env[url], 'token': env[url.replace('URL', 'TOKEN')], 'metrics': env[f'OS_METRICS_{url[11:]}'],
                'pprb3_versions': env[f'PPRB3_VERSIONS_{url[11:]}']} for url in env if '_URL_' in url}
