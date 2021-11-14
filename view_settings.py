#!/usr/bin/python3

import time
import json
import requests
from functools import reduce
from pymongo import MongoClient
# from bson.objectid import ObjectId
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def json_read(json_object: dict):
    print(json.dumps(json_object, indent=4))

def visiableSetting():
    def cmdb_api(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
        cmdb_api_url: str = "https://cmdb.common.gos-tech.xyz/rest/"
        headers_cmdb_api: dict = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token
        }
        return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                           data=json.dumps(payload)).content)


    def get_cmdb_token() -> str:
        from env import cmdb_login, cmdb_password
        auth_payload: dict = {
            "user_name": cmdb_login,
            "password": cmdb_password
        }
        # check_cmdb_auth = cmdb_api('GET', 'users/')
        # print(check_cmdb_auth)
        user_info = cmdb_api('POST', 'auth/login', payload=auth_payload)
        return user_info['token'], user_info['user']['public_id']


    cmdb_token, id_user = get_cmdb_token()

    number_of_tread = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)


    def get_info_from_all_page(cmdb_item: str) -> tuple:
        numbers_of_pages = cmdb_api('GET', f"{cmdb_item}/", cmdb_token)['pager']['total_pages']

        def get_info_from_one_page(page_number: int):
            return cmdb_api('GET', f'{cmdb_item}/?page={page_number}', cmdb_token)

        full_info = list()
        with ThreadPoolExecutor(max_workers=number_of_tread(numbers_of_pages)) as executor:
            for page_info in executor.map(get_info_from_one_page, range(1, numbers_of_pages + 1)):
                full_info.append(page_info)
        return tuple(full_info)


    cmdb_projects = get_info_from_all_page('types')
    cmdb_projects_vm = dict(type='vm', items=list())
    cmdb_projects_os = dict(type='os', items=list())

    for item in cmdb_projects:
        for type in item['results']:
            if type['render_meta']['sections'][0]['fields'][0] == 'name':
                cmdb_projects_vm['items'].append(type['public_id'])
            elif type['render_meta']['sections'][0]['fields'][0] == 'namespace':
                cmdb_projects_os['items'].append(type['public_id'])


    cmdb_users = get_info_from_all_page('users')
    cmdb_users = reduce(lambda x, y: x + y,
                        map(lambda foo: tuple(map(lambda bar: bar['public_id'], foo['results'])), cmdb_users))
# cmdb_users = (35, 19, 13, 9, 17)

    connection_sring = 'mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb'
    cluster = MongoClient(connection_sring)

    db = cluster['cmdb']

# users_settings = max(filter(lambda x: x['name'] == 'management.users.settings', collection))
    for user_id in cmdb_users:

        users_settings = db.get_collection('management.users.settings')
        visibleSettings = users_settings.find({'user_id': user_id})

        viewSettings = list()
        for settings in visibleSettings:
            viewSettings.append(settings)
        del visibleSettings


        def visibleSettings(projects: list):
            viewSettingsForCreate = list()
            for cmdb_type in projects['items']:
                for settings in viewSettings:

                    if f'framework-object-type-{cmdb_type}' == settings['resource']:
                        if 'currentState' in settings['payloads'][0]:
                            if 'fields.name' in settings['payloads'][0]['currentState']["visibleColumns"]:

                                visibleColumnsVm = [
                                    "fields.name",
                                    "fields.vm-name",
                                    "fields.os-type",
                                    "fields.flavor",
                                    "fields.cpu",
                                    "fields.ram",
                                    "fields.disk",
                                    "fields.additional-disk",
                                    "fields.local-ip",
                                    "fields.public-ip",
                                    "fields.state",
                                    "fields.creation-date",
                                    "actions"
                                ]

                                foo = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                bar = set(visibleColumnsVm)

                                if (foo - bar) or (bar - foo) or settings['payloads'][0]['currentState']['pageSize'] != 200:
                                    settings['payloads'][0]['currentState']['pageSize'] = 200
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visibleColumnsVm
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                    time.sleep(0.5)

                            elif 'fields.namespace' in settings['payloads'][0]['currentState']["visibleColumns"]:

                                visibleColumnsOs = [
                                    "fields.namespace",
                                    "fields.limits.cpu-hard",
                                    "fields.limits.cpu-used",
                                    "fields.cores-usage",
                                    "fields.limits.memory-hard",
                                    "fields.limits.memory-used",
                                    "fields.memory-usage",
                                    "actions"
                                ]

                                baz = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                zip = set(visibleColumnsOs)

                                if (baz - zip) or (zip - baz) or settings['payloads'][0]['currentState']['pageSize'] != 50:
                                    settings['payloads'][0]['currentState']['pageSize'] = 50
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visibleColumnsOs
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                        else:
                            if projects['type'] == 'vm':
                                payloads_vm = [
                                    {
                                        "id": "table-objects-type",
                                        "tableStates": [],
                                        "currentState": {
                                            "name": "",
                                            "page": 1,
                                            "pageSize": 200,
                                            "sort": {
                                                "name": "public_id",
                                                "order": -1
                                            },
                                            "visibleColumns": [
                                                "fields.name",
                                                "fields.vm-name",
                                                "fields.os-type",
                                                "fields.flavor",
                                                "fields.cpu",
                                                "fields.ram",
                                                "fields.disk",
                                                "fields.additional-disk",
                                                "fields.local-ip",
                                                "fields.public-ip",
                                                "fields.state",
                                                "fields.creation-date",
                                                "actions"
                                            ]
                                        }
                                    }
                                ]
                                settings['payloads'] = payloads_vm
                            elif projects['type'] == 'os':
                                payloads_os = [
                                    {
                                        "id": "table-objects-type",
                                        "tableStates": [],
                                        "currentState": {
                                            "name": "",
                                            "page": 1,
                                            "pageSize": 50,
                                            "sort": {
                                                "name": "public_id",
                                                "order": -1
                                            },
                                            "visibleColumns": [
                                                "fields.namespace",
                                                "fields.limits.cpu-hard",
                                                "fields.limits.cpu-used",
                                                "fields.cores-usage",
                                                "fields.limits.memory-hard",
                                                "fields.limits.memory-used",
                                                "fields.memory-usage",
                                                "actions"
                                            ]
                                        }
                                    }
                                ]
                                settings['payloads'] = payloads_os
                            update_view_settings = users_settings.update_one({"_id": settings['_id']}, {"$set": settings})
                            print(update_view_settings.raw_result)

                if f'framework-object-type-{cmdb_type}' not in map(lambda x: x['resource'], viewSettings):
                    if projects['type'] == 'os':

                        settings_view_os = {
                            "setting_type": "APPLICATION",
                            "resource": "framework-object-type-1009",
                            "user_id": 17,
                            "payloads": [
                                {
                                    "id": "table-objects-type",
                                    "tableStates": [],
                                    "currentState": {
                                        "name": "",
                                        "page": 1,
                                        "pageSize": 50,
                                        "sort": {
                                            "name": "public_id",
                                            "order": -1
                                        },
                                        "visibleColumns": [
                                            "fields.namespace",
                                            "fields.limits.cpu-hard",
                                            "fields.limits.cpu-used",
                                            "fields.cores-usage",
                                            "fields.limits.memory-hard",
                                            "fields.limits.memory-used",
                                            "fields.memory-usage",
                                            "actions"
                                        ]
                                    }
                                }
                            ]
                        }

                        settings_view_os['resource'] = f"framework-object-type-{cmdb_type}"
                        settings_view_os['user_id'] = user_id
                        viewSettingsForCreate.append(settings_view_os)

                    elif projects['type'] == 'vm':

                        settings_view_vm = {
                            "setting_type": "APPLICATION",
                            "resource": "framework-object-type-1009",
                            "user_id": 17,
                            "payloads": [
                                {
                                    "id": "table-objects-type",
                                    "tableStates": [],
                                    "currentState": {
                                        "name": "",
                                        "page": 1,
                                        "pageSize": 200,
                                        "sort": {
                                            "name": "public_id",
                                            "order": -1
                                        },
                                        "visibleColumns": [
                                            "fields.name",
                                            "fields.vm-name",
                                            "fields.os-type",
                                            "fields.flavor",
                                            "fields.cpu",
                                            "fields.ram",
                                            "fields.disk",
                                            "fields.additional-disk",
                                            "fields.local-ip",
                                            "fields.public-ip",
                                            "fields.state",
                                            "fields.creation-date",
                                            "actions"
                                        ]
                                    }
                                }
                            ]
                        }

                        settings_view_vm['resource'] = f"framework-object-type-{cmdb_type}"
                        settings_view_vm['user_id'] = user_id
                        viewSettingsForCreate.append(settings_view_vm)

            if viewSettingsForCreate:
                create_view_settings = users_settings.insert_many(viewSettingsForCreate)
                for new_object in create_view_settings.inserted_ids:
                    print(f'Create new settings {new_object} for user {user_id}')

        visibleSettings(cmdb_projects_vm)
        visibleSettings(cmdb_projects_os)