#!/usr/local/bin/python3

import json
import requests
import datetime
from loguru import logger
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor

from env import portal_info, mongo_db_url
from pymongo import MongoClient


def get_mongodb_objects(collection: str, find: dict = None) -> tuple:
    """
    Func to work with DataGerry mongodb
    :param collection:
    :param find:
    :return:
    """
    mongo_objects = MongoClient(mongo_db_url)['cmdb'].get_collection(collection)
    if find:
        return tuple(mongo_objects.find(find))
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


def dg_api(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
    """
    Func to use DataGerry rest-api
    :param method:
    :param api_method:
    :param token:
    :param payload:
    :return:
    """
    from env import dg_url
    headers: dict = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }

    if api_method == "POST":
        logger.info(f'CREATE {method}')
    elif api_method == "PUT":
        logger.info(f'UPDATE {method}')
    elif api_method == "DELETE":
        logger.info(f'DELETE {method}')
    return json.loads(requests.request(method, dg_url + api_method, headers=headers, data=json.dumps(payload)).content)


def get_dg_token() -> tuple[str, int]:
    """
    Function to get app token and user id
    :return:
    """
    from env import dg_login, dg_password
    payload_auth: dict = {
        "user_name": dg_login,
        "password": dg_password
    }
    user_info: dict = dg_api("POST", "auth/login", payload=payload_auth)
    logger.info(
        f'''Create DG auth-token for "{user_info["user"]["user_name"]}", user-id -> {user_info['user']['public_id']}'''
    )
    return user_info["token"], user_info["user"]["public_id"]


def get_k8s_info() -> list:
    """
    Func to get json from ose exporter
    :return:
    """
    info = list()
    for metrics_url in portal_info["metrics"].split(";"):
        info.append(json.loads(requests.request("GET", metrics_url.strip(), timeout=3).content)['data']['result'])
    # return json.loads(requests.request("GET", portal_info["metrics"]).content)
    return info


# thread_count = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)
# def thread_count(x: int) -> int: return int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)
def thread_count(x: int) -> int: return int(x) if x < 10 and x else int((x + 1) ** 0.7)


def get_all_jsons(dg_item: str, dg_token: str) -> tuple:
    """
    Function to get different types of cmdb data in one tuple
    :param dg_item:
    :param dg_token:
    :return:
    """
    json_count = dg_api("GET", "%s/" % dg_item, dg_token)["pager"]["total_pages"]

    def get_one_json(page_number: int):
        return dg_api("GET", "%s/?page=%s" % (dg_item, page_number), dg_token)

    full_info = list()
    # with ThreadPoolExecutor(max_workers=thread_count(json_count)) as executor:
    with ThreadPoolExecutor(max_workers=1) as executor:
        for page_info in executor.map(get_one_json, range(1, json_count + 1)):
            full_info.append(page_info)
    return tuple(full_info)


def create_category(name: str, label: str, icon: str, dg_token: str, parent: int = None) -> dict:
    """
    Function to create categories in CMDB
    :param name:
    :param label:
    :param icon:
    :param dg_token:
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

    return dg_api("POST", "categories/", dg_token, payload_category_tmp)


def category_id(category_name: str, category_label: str, category_icon: str, dg_token: str, dg_categories: tuple,
                parent_category: int = None) -> dict:
    """
    Func to create category in cmdb
    :param category_name:
    :param category_label:
    :param category_icon:
    :param dg_token:
    :param dg_categories:
    :param parent_category:
    :return:
    """

    if not any(tuple(map(lambda y: y["name"] == category_name, dg_categories))):
        result: dict = create_category(category_name, category_label, category_icon, dg_token, parent_category)
        return {
            "public_id": result["raw"]["public_id"],
            "name": result["raw"]["name"],
            "label": result["raw"]["label"],
            "types": result["raw"]["types"]
        }
    else:
        result: dict = max(filter(lambda y: y["name"] == category_name, dg_categories))
        return {
            "public_id": result["public_id"],
            "name": result["name"],
            "label": result["label"],
            "types": result["types"]
        }


def portal_api(api_name: str) -> dict:
    """
    Func to work with Portal REST-API
    :param api_name:
    :return: dict
    """
    headers: dict = {
        "user-agent": 'CMDB',
        "Content-type": 'application/json',
        "Accept": "text/plain",
        "authorization": "Token %s" % portal_info["token"]
    }
    response = requests.get("%s/api/v1/%s" % (portal_info["url"], api_name), headers=headers, verify=False)
    return dict(stdout=json.loads(response.content), status_code=response.status_code)


###############################################################


def get_label(labels: dict, label: str) -> str:
    if 'labels' in labels:
        if label in labels:
            return labels[label]
        elif label in labels['labels']:
            return labels['labels'][label]
        else:
            return ''
    else:
        if label in labels:
            return labels[label]
        else:
            return ''


def check_resolves(dns_name: str) -> bool:
    """
    Function for checking resolving dns names
    """
    try:
        socket.gethostbyname(dns_name)
        return True
    except socket.error as Error:
        logger.error(dns_name, Error)
        return False
