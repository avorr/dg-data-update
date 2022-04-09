#!/usr/bin/python3

import os
import json
from typing import Tuple, Any

import requests
import datetime
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# from tools import *
from env import portal_info, mongo_db_url
from pymongo import MongoClient

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_mongodb_objects(collection: str, find: dict = None) -> tuple:
    """
    Func to work with DataGerry mongodb
    :param collection:
    :param find:
    :return:
    """
    # mongo_db = MongoClient('mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb')['cmdb']
    mongo_db = MongoClient(mongo_db_url)['cmdb']
    # mongo_db = MongoClient('mongodb://172.26.107.101:30039/cmdb')['cmdb']
    # mongo_objects = mongo_db.get_collection('framework.%s' % collection)
    mongo_objects = mongo_db.get_collection(collection)
    if find:
        # mongo_objects = mongo_db.get_collection(collection)
        return tuple(mongo_objects.find(find))
    # mongo_objects = mongo_db.get_collection(collection)
    return tuple(mongo_objects.find())


def json_serial(obj: datetime) -> str:
    """
    JSON serializer for objects not serializable by default json code
    :param obj: datetime
    :return: str
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def cmdb_api(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
    """
    Func to use DataGerry rest-api
    :param method:
    :param api_method:
    :param token:
    :param payload:
    :return:
    """
    cmdb_api_url: str = os.environ["DATA_GERRY_CMDB_URL"]
    headers_cmdb_api: dict = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                       data=json.dumps(payload)).content)


# def get_dg_token() -> tuple[str, str]:
def get_dg_token() -> str:
    """
    Function to get app token and user id
    :return:
    """
    from env import cmdb_login, cmdb_password
    payload_auth: dict = {
        "user_name": cmdb_login,
        "password": cmdb_password
    }
    user_info = cmdb_api('POST', 'auth/login', payload=payload_auth)
    return user_info['token'], user_info['user']['public_id']


# thread_count = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)
# def thread_count(x: int) -> int: return int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)
def thread_count(x: int) -> int: return int(x) if x < 10 and x else int((x + 1) ** 0.7)


def get_all_jsons(dg_item: str, cmdb_token: str) -> tuple:
    """
    Function to get different types of cmdb data in one tuple
    :param dg_item:
    :param cmdb_token:
    :return:
    """
    json_count = cmdb_api('GET', f"{dg_item}/", cmdb_token)['pager']['total_pages']

    def get_one_json(page_number: int):
        return cmdb_api('GET', f'{dg_item}/?page={page_number}', cmdb_token)

    full_info = list()
    # with ThreadPoolExecutor(max_workers=thread_count(json_count)) as executor:
    with ThreadPoolExecutor(max_workers=1) as executor:
        for page_info in executor.map(get_one_json, range(1, json_count + 1)):
            full_info.append(page_info)
    return tuple(full_info)


def create_category(name: str, label: str, icon: str, cmdb_token: str, parent: int = None) -> dict:
    """
    Function to create categories in CMDB
    :param name:
    :param label:
    :param icon:
    :param cmdb_token:
    :param parent:
    :return:
    """
    payload_category_tmp: dict = {
        "name": name,
        "label": label,
        "meta": {
            "icon": icon,
            "order": None
        },
        "parent": parent,
        "types": list()
    }

    return cmdb_api('POST', 'categories/', cmdb_token, payload_category_tmp)


def category_id(category_name: str, category_label: str, category_icon: str, cmdb_token: str, dg_categories: tuple,
                parent_category: int = None) -> dict:
    """
    Func to create category in cmdb
    :param category_name:
    :param category_label:
    :param category_icon:
    :param cmdb_token:
    :param dg_categories:
    :param parent_category:
    :return:
    """

    if not any(map(lambda y: y['name'] == category_name, dg_categories)):
        print(True)
        result: dict = create_category(category_name, category_label, category_icon, cmdb_token, parent_category)
        return {
            'public_id': result['raw']['public_id'],
            'name': result['raw']['name'],
            'label': result['raw']['label'],
            'types': result['raw']['types']
        }
    else:
        result: dict = max(filter(lambda y: y['name'] == category_name, dg_categories))
        return {
            'public_id': result['public_id'],
            'name': result['name'],
            'label': result['label'],
            'types': result['types']
        }


def portal_api(api_name: str, portal_name: str) -> dict:
    """
    Func to work with Portal REST-API
    :param api_name:
    :param portal_name:
    :return: dict
    """
    headers: dict = {
        'user-agent': 'CMDB',
        'Content-type': 'application/json',
        'Accept': 'text/plain',
        'authorization': 'Token %s' % portal_info[portal_name]['token']
    }
    response = requests.get('%s/api/v1/%s' % (portal_info[portal_name]['url'], api_name), headers=headers, verify=False)
    return dict(stdout=json.loads(response.content), status_code=response.status_code)
