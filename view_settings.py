#!/usr/bin/python3

import time
import json
import requests
from functools import reduce
from pymongo import MongoClient
from tools import *
# from bson.objectid import ObjectId
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def visiableSetting():
    def cmdb_api(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
        cmdb_api_url: str = "https://cmdb.common.gos-tech.xyz/rest/"
        headers_cmdb_api: dict = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token
        }
        return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                           data=json.dumps(payload)).content)

    def getCmdbToken() -> str:
        from env import cmdb_login, cmdb_password
        auth_payload: dict = {
            "user_name": cmdb_login,
            "password": cmdb_password
        }
        # check_cmdb_auth = cmdb_api('GET', 'users/')
        # print(check_cmdb_auth)
        user_info = cmdb_api('POST', 'auth/login', payload=auth_payload)
        return user_info['token'], user_info['user']['public_id']

    cmdb_token, id_user = getCmdbToken()

    number_of_tread = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)

    def getInfoFromAllPage(cmdb_item: str) -> tuple:
        numbers_of_pages = cmdb_api('GET', f"{cmdb_item}/", cmdb_token)['pager']['total_pages']

        def get_info_from_one_page(page_number: int):
            return cmdb_api('GET', f'{cmdb_item}/?page={page_number}', cmdb_token)

        full_info = list()
        # with ThreadPoolExecutor(max_workers=number_of_tread(numbers_of_pages)) as executor:
        with ThreadPoolExecutor(max_workers=1) as executor:
            for page_info in executor.map(get_info_from_one_page, range(1, numbers_of_pages + 1)):
                full_info.append(page_info)
        return tuple(full_info)

    cmdb_projects = getInfoFromAllPage('types')
    cmdb_projects_vm = dict(type='vm', items=list())
    cmdb_projects_os = dict(type='os', items=list())
    cmdb_projects_label = dict(type='label', items=list())
    cmdb_projects_version = dict(type='version', items=list())
    cmdb_projects_vcd = dict(type='vcd', items=list())

    for item in cmdb_projects:
        for type in item['results']:
            if type['render_meta']['sections'][0]['fields'][2] == 'os-type':
                cmdb_projects_vm['items'].append(type['public_id'])
            elif type['render_meta']['sections'][0]['fields'][1] == 'limits.cpu-hard':
                cmdb_projects_os['items'].append(type['public_id'])
            elif type['render_meta']['sections'][0]['fields'][3] == 'SUBSYSTEM':
                cmdb_projects_label['items'].append(type['public_id'])
            elif type['render_meta']['sections'][0]['fields'][4] == 'version':
                cmdb_projects_version['items'].append(type['public_id'])
            elif type['render_meta']['sections'][0]['fields'][1] == 'datacenter-name':
                cmdb_projects_vcd['items'].append(type['public_id'])

    cmdb_users = getInfoFromAllPage('users')
    cmdb_users = reduce(lambda x, y: x + y,
                        map(lambda foo: tuple(map(lambda bar: bar['public_id'], foo['results'])), cmdb_users))
    # cmdb_users = (35, 19, 13, 9, 17)
    # cmdb_users = (10,)

    connection_sring = 'mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb'
    cluster = MongoClient(connection_sring)

    db = cluster['cmdb']

    # exLabels = {
    #     _id: ObjectId('61c3b6efbdb9a797864deb01'),
    #     setting_type: 'APPLICATION',
    #     resource: 'framework-object-type-98',
    #     user_id: 17,
    #     payloads: [
    #         {
    #             id: 'table-objects-type',
    #             tableStates: [],
    #             currentState: {
    #                 name: '',
    #                 page: 1,
    #                 pageSize: 500,
    #                 sort: {
    #                     name: 'public_id',
    #                     order: -1
    #                 },
    #                 visibleColumns: [
    #                     'fields.namespace',
    #                     'fields.name',
    #                     'fields.app',
    #                     'fields.SUBSYSTEM',
    #                     'fields.deployment',
    #                     'fields.deploymentconfig',
    #                     'fields.deployDate',
    #                     'fields.distribVersion',
    #                     'fields.version',
    #                     'fields.security.istio.io/tlsMode',
    #                     'fields.jenkinsDeployUser',
    #                     'actions'
    #                 ]
    #             }
    #         }
    #     ]
    # }

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
                            if 'fields.additional-disk' in settings['payloads'][0]['currentState']["visibleColumns"]:

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
                                    "fields.tags",
                                    "fields.state",
                                    "fields.creation-date",
                                    "actions"
                                ]

                                foo = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                bar = set(visibleColumnsVm)

                                if (foo - bar) or (bar - foo) or settings['payloads'][0]['currentState'][
                                    'pageSize'] != 200:
                                    settings['payloads'][0]['currentState']['pageSize'] = 200
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visibleColumnsVm
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                    time.sleep(0.5)

                            elif 'fields.limits.cpu-hard' in settings['payloads'][0]['currentState']["visibleColumns"]:

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

                                if (baz - zip) or (zip - baz) or settings['payloads'][0]['currentState'][
                                    'pageSize'] != 50:
                                    settings['payloads'][0]['currentState']['pageSize'] = 50
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visibleColumnsOs
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                del baz, zip

                            elif 'fields.SUBSYSTEM' in settings['payloads'][0]['currentState']["visibleColumns"]:
                                # print(settings['payloads'][0]['currentState']["visibleColumns"])

                                visibleColumnsLabel = [
                                    'fields.namespace',
                                    'fields.name',
                                    'fields.app',
                                    'fields.SUBSYSTEM',
                                    'fields.deployment',
                                    'fields.deploymentconfig',
                                    'fields.deployDate',
                                    'fields.distribVersion',
                                    'fields.version',
                                    'fields.security.istio.io/tlsMode',
                                    'fields.jenkinsDeployUser',
                                    'actions'
                                ]

                                bat = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                quux = set(visibleColumnsLabel)

                                if (bat - quux) or (quux - bat) or settings['payloads'][0]['currentState'][
                                    'pageSize'] != 500:
                                    settings['payloads'][0]['currentState']['pageSize'] = 500
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visibleColumnsLabel
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                del bat, quux


                            elif 'fields.datacenter-name' in settings['payloads'][0]['currentState']["visibleColumns"]:
                                # print(settings['payloads'][0]['currentState']["visibleColumns"])

                                visibleColumnsVcd = [
                                    'fields.name',
                                    'fields.datacenter-name',
                                    'fields.networks',
                                    'fields.dns-nameservers',
                                    'actions'
                                ]

                                bat = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                quux = set(visibleColumnsVcd)

                                if (bat - quux) or (quux - bat) or settings['payloads'][0]['currentState'][
                                    'pageSize'] != 100:
                                    settings['payloads'][0]['currentState']['pageSize'] = 100
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visibleColumnsVcd
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                del bat, quux

                            elif 'fields.tag' in settings['payloads'][0]['currentState']["visibleColumns"]:
                                visibleColumnsVersion = [
                                    'fields.name',
                                    'fields.vm-name',
                                    'fields.local-ip',
                                    'fields.tag',
                                    'fields.version',
                                    'actions'
                                ]

                                bat = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                quux = set(visibleColumnsVersion)

                                if (bat - quux) or (quux - bat) or \
                                        settings['payloads'][0]['currentState']['pageSize'] != 50:
                                    settings['payloads'][0]['currentState']['pageSize'] = 50
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visibleColumnsVersion
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                del bat, quux


                        else:
                            if projects['type'] == 'vm':
                                print('######' * 100, '\nTHIS BLOCK IS WORKING\n', '######' * 100)
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
                                                "fields.tags",
                                                "fields.state",
                                                "fields.creation-date",
                                                "actions"
                                            ]
                                        }
                                    }
                                ]
                                settings['payloads'] = payloads_vm
                            elif projects['type'] == 'os':
                                print('######' * 100, '\nTHIS BLOCK IS WORKING\n', '######' * 100)
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

                            elif projects['type'] == 'label':
                                print('######' * 100, '\nTHIS BLOCK IS WORKING\n', '######' * 100)
                                payloads_label = [
                                    {
                                        "id": "table-objects-type",
                                        "tableStates": [],
                                        "currentState": {
                                            "name": "",
                                            "page": 1,
                                            "pageSize": 500,
                                            "sort": {
                                                "name": "public_id",
                                                "order": -1
                                            },
                                            "visibleColumns": [
                                                'fields.namespace',
                                                'fields.name',
                                                'fields.app',
                                                'fields.SUBSYSTEM',
                                                'fields.deployment',
                                                'fields.deploymentconfig',
                                                'fields.deployDate',
                                                'fields.distribVersion',
                                                'fields.version',
                                                'fields.security.istio.io/tlsMode',
                                                'fields.jenkinsDeployUser',
                                                'actions'
                                            ]
                                        }
                                    }
                                ]
                                settings['payloads'] = payloads_label


                            elif projects['type'] == 'version':
                                print('######' * 100, '\nTHIS BLOCK IS WORKING\n', '######' * 100)
                                payloads_version = [
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
                                                'fields.name',
                                                'fields.vm-name',
                                                'fields.local-ip',
                                                'fields.tag',
                                                'fields.version',
                                                'actions'
                                            ]
                                        }
                                    }
                                ]
                                settings['payloads'] = payloads_version

                            elif projects['type'] == 'vcd':
                                print('######' * 100, '\nTHIS BLOCK IS WORKING\n', '######' * 100)
                                payloads_vcd = [
                                    {
                                        "id": "table-objects-type",
                                        "tableStates": [],
                                        "currentState": {
                                            "name": "",
                                            "page": 1,
                                            "pageSize": 100,
                                            "sort": {
                                                "name": "public_id",
                                                "order": -1
                                            },
                                            "visibleColumns": [
                                                'fields.name',
                                                'fields.datacenter-name',
                                                'fields.networks',
                                                'fields.dns-nameservers',
                                                'actions'
                                            ]
                                        }
                                    }
                                ]
                                settings['payloads'] = payloads_vcd

                            update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                             {"$set": settings})
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
                                            "fields.tags",
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

                    elif projects['type'] == 'label':

                        settings_view_label = {
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
                                        "pageSize": 500,
                                        "sort": {
                                            "name": "public_id",
                                            "order": -1
                                        },
                                        "visibleColumns": [
                                            "fields.namespace",
                                            "fields.name",
                                            "fields.app",
                                            "fields.SUBSYSTEM",
                                            "fields.deployment",
                                            "fields.deploymentconfig",
                                            "fields.deployDate",
                                            "fields.distribVersion",
                                            "fields.version",
                                            "fields.security.istio.io/tlsMode",
                                            "fields.jenkinsDeployUser",
                                            "actions"
                                        ]
                                    }
                                }
                            ]
                        }

                        # users_settings = max(filter(lambda x: x['name'] == 'management.users.settings', collection))

                        settings_view_label['resource'] = f"framework-object-type-{cmdb_type}"
                        settings_view_label['user_id'] = user_id
                        viewSettingsForCreate.append(settings_view_label)

                    elif projects['type'] == 'version':
                        settings_view_version = {
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
                                            "fields.name",
                                            "fields.vm-name",
                                            "fields.local-ip",
                                            "fields.tag",
                                            "fields.version",
                                            "actions"
                                        ]
                                    }
                                }
                            ]
                        }
                        # users_settings = max(filter(lambda x: x['name'] == 'management.users.settings', collection))
                        settings_view_version['resource'] = f"framework-object-type-{cmdb_type}"
                        settings_view_version['user_id'] = user_id
                        viewSettingsForCreate.append(settings_view_version)

                    elif projects['type'] == 'vcd':

                        settings_view_vcd = {
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
                                        "pageSize": 100,
                                        "sort": {
                                            "name": "public_id",
                                            "order": -1
                                        },
                                        "visibleColumns": [
                                            "fields.name",
                                            "fields.datacenter-name",
                                            "fields.networks",
                                            "fields.dns-nameservers",
                                            "actions"
                                        ]
                                    }
                                }
                            ]
                        }
                        # users_settings = max(filter(lambda x: x['name'] == 'management.users.settings', collection))
                        settings_view_vcd['resource'] = f"framework-object-type-{cmdb_type}"
                        settings_view_vcd['user_id'] = user_id
                        viewSettingsForCreate.append(settings_view_vcd)

            if viewSettingsForCreate:
                create_view_settings = users_settings.insert_many(viewSettingsForCreate)
                for new_object in create_view_settings.inserted_ids:
                    print(f'Create new settings {new_object} for user {user_id}')

        visibleSettings(cmdb_projects_vm)
        visibleSettings(cmdb_projects_os)
        visibleSettings(cmdb_projects_label)
        visibleSettings(cmdb_projects_version)
        visibleSettings(cmdb_projects_vcd)


if __name__ == '__main__':
    visiableSetting()
