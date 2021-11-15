#!/usr/bin/python3

import os

cmdb_login: str = os.environ['CMDB_CRED_USR']
cmdb_password: str = os.environ['CMDB_CRED_PSW']

fortiLogin: str = os.environ['FORTI_CRED_USR']
fortiPassword: str = os.environ['FORTI_CRED_PSW']

HOST: str = os.environ['HOST']


env: dict = {url: os.environ[url] for url in os.environ if 'PORTAL_' in url or 'OS_METRICS_' in url}

portal_info: dict = \
    {url[11:]: {'url': env[url], 'token': env[url.replace('URL', 'TOKEN')], 'metrics': env[f'OS_METRICS_{url[11:]}']}
     for url in env if '_URL_' in url}