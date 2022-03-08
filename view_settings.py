#!/usr/bin/python3

import time
import json
import requests
from functools import reduce
from pymongo import MongoClient
from vm_passport import get_mongodb_objects
from tools import *
# from bson.objectid import ObjectId
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def visible_settings():
    """
    Main func for creating visible settings in cmdb
    :return: None
    """

    def cmdb_api(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
        """
        Func to work with cmdb api
        :param method:
        :param api_method:
        :param token:
        :param payload:
        :return: dick
        """
        cmdb_api_url: str = "https://cmdb.common.gos-tech.xyz/rest/"
        headers_cmdb_api: dict = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token
        }
        return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                           data=json.dumps(payload)).content)

    def get_dg_token() -> str:
        from env import cmdb_login, cmdb_password
        auth_payload: dict = {
            "user_name": cmdb_login,
            "password": cmdb_password
        }
        # check_cmdb_auth = cmdb_api('GET', 'users/')
        # print(check_cmdb_auth)
        user_info = cmdb_api('POST', 'auth/login', payload=auth_payload)
        return user_info['token'], user_info['user']['public_id']

    cmdb_token, id_user = get_dg_token()

    number_of_tread = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)

    def get_all_jsons(cmdb_item: str) -> tuple:
        numbers_of_pages = cmdb_api('GET', f"{cmdb_item}/", cmdb_token)['pager']['total_pages']

        def get_info_from_one_page(page_number: int):
            return cmdb_api('GET', f'{cmdb_item}/?page={page_number}', cmdb_token)

        full_info = list()
        # with ThreadPoolExecutor(max_workers=number_of_tread(numbers_of_pages)) as executor:
        with ThreadPoolExecutor(max_workers=1) as executor:
            for page_info in executor.map(get_info_from_one_page, range(1, numbers_of_pages + 1)):
                full_info.append(page_info)
        return tuple(full_info)

    # cmdb_projects = get_all_jsons('types')

    cmdb_projects: tuple = get_mongodb_objects('framework.types')

    cmdb_projects_vm: dict = {
        'type': 'vm',
        'items': list()
    }
    cmdb_projects_os: dict = {
        'type': 'os',
        'items': list()
    }
    cmdb_projects_label: dict = {
        'type': 'label',
        'items': list()
    }
    cmdb_projects_version: dict = {
        'type': 'version',
        'items': list()
    }
    cmdb_projects_vdc: dict = {
        'type': 'vcd',
        'items': list()
    }
    cmdb_projects_release: dict = {
        'type': 'release',
        'items': list()
    }

    # for item in cmdb_projects:
    #     for type in item['results']:
    #         if type['render_meta']['sections'][0]['fields'][2] == 'os-type':
    #             cmdb_projects_vm['items'].append(type['public_id'])
    #         elif type['render_meta']['sections'][0]['fields'][1] == 'limits.cpu-hard':
    #             cmdb_projects_os['items'].append(type['public_id'])
    #         elif type['render_meta']['sections'][0]['fields'][3] == 'SUBSYSTEM':
    #             cmdb_projects_label['items'].append(type['public_id'])
    #         elif type['render_meta']['sections'][0]['fields'][4] == 'version':
    #             cmdb_projects_version['items'].append(type['public_id'])
    #         elif type['render_meta']['sections'][0]['fields'][1] == 'datacenter-name':
    #             cmdb_projects_vdc['items'].append(type['public_id'])
    #         elif type['render_meta']['sections'][0]['fields'][0] == 'platform-path':
    #             cmdb_projects_release['items'].append(type['public_id'])

    for type in cmdb_projects:
        if type['render_meta']['sections'][0]['fields'][2] == 'os-type':
            cmdb_projects_vm['items'].append(type['public_id'])
        elif type['render_meta']['sections'][0]['fields'][1] == 'limits.cpu-hard':
            cmdb_projects_os['items'].append(type['public_id'])
        elif type['render_meta']['sections'][0]['fields'][3] == 'SUBSYSTEM':
            cmdb_projects_label['items'].append(type['public_id'])
        elif type['render_meta']['sections'][0]['fields'][4] == 'version':
            cmdb_projects_version['items'].append(type['public_id'])
        elif type['render_meta']['sections'][0]['fields'][1] == 'datacenter-name':
            cmdb_projects_vdc['items'].append(type['public_id'])
        elif type['render_meta']['sections'][0]['fields'][0] == 'platform-path':
            cmdb_projects_release['items'].append(type['public_id'])


    # cmdb_users = get_all_jsons('users')
    cmdb_users: tuple = get_mongodb_objects('management.users')
    cmdb_users = tuple(map(lambda x: x['public_id'], cmdb_users))

    # cmdb_users = reduce(lambda x, y: x + y, map(lambda foo: tuple(map(lambda bar: bar['public_id'], foo['results'])), cmdb_users))

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
        visible_settings = users_settings.find({'user_id': user_id})

        view_settings = list()
        for settings in visible_settings:
            view_settings.append(settings)
        del visible_settings

        def create_settings(projects: list) -> None:
            view_settings_for_create = list()
            for cmdb_type in projects['items']:
                for settings in view_settings:

                    if f'framework-object-type-{cmdb_type}' == settings['resource']:
                        if 'currentState' in settings['payloads'][0]:
                            if 'fields.additional-disk' in settings['payloads'][0]['currentState']["visibleColumns"]:

                                visible_columns_vm = [
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
                                bar = set(visible_columns_vm)

                                if (foo - bar) or (bar - foo) or settings['payloads'][0]['currentState'][
                                    'pageSize'] != 200:
                                    settings['payloads'][0]['currentState']['pageSize'] = 200
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visible_columns_vm
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                    time.sleep(0.5)

                            elif 'fields.limits.cpu-hard' in settings['payloads'][0]['currentState']["visibleColumns"]:

                                visible_columns_os = [
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
                                zip = set(visible_columns_os)

                                if (baz - zip) or (zip - baz) or \
                                        settings['payloads'][0]['currentState']['pageSize'] != 50:
                                    settings['payloads'][0]['currentState']['pageSize'] = 50
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visible_columns_os
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                del baz, zip

                            elif 'fields.SUBSYSTEM' in settings['payloads'][0]['currentState']["visibleColumns"]:
                                # print(settings['payloads'][0]['currentState']["visibleColumns"])

                                visible_columns_label = [
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
                                quux = set(visible_columns_label)

                                if (bat - quux) or (quux - bat) or \
                                        settings['payloads'][0]['currentState']['pageSize'] != 500:
                                    settings['payloads'][0]['currentState']['pageSize'] = 500
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visible_columns_label
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                del bat, quux


                            elif 'fields.datacenter-name' in settings['payloads'][0]['currentState']["visibleColumns"]:
                                # print(settings['payloads'][0]['currentState']["visibleColumns"])

                                visible_columns_vcd = [
                                    'fields.name',
                                    'fields.datacenter-name',
                                    'fields.networks',
                                    'fields.dns-nameservers',
                                    'actions'
                                ]

                                bat = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                quux = set(visible_columns_vcd)

                                if (bat - quux) or (quux - bat) or \
                                        settings['payloads'][0]['currentState']['pageSize'] != 100:
                                    settings['payloads'][0]['currentState']['pageSize'] = 100
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visible_columns_vcd
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                del bat, quux

                            elif 'fields.tag' in settings['payloads'][0]['currentState']["visibleColumns"]:
                                visible_columns_version = [
                                    'fields.name',
                                    'fields.vm-name',
                                    'fields.local-ip',
                                    'fields.tag',
                                    'fields.version',
                                    'actions'
                                ]

                                bat = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                quux = set(visible_columns_version)

                                if (bat - quux) or (quux - bat) or \
                                        settings['payloads'][0]['currentState']['pageSize'] != 100:
                                    settings['payloads'][0]['currentState']['pageSize'] = 100
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visible_columns_version
                                    update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                                     {"$set": settings})
                                    print(update_view_settings.raw_result)
                                del bat, quux


                            elif 'fields.platform-path' in settings['payloads'][0]['currentState']["visibleColumns"]:

                                visible_columns_release: list = [
                                    "fields.platform-path",
                                    "fields.tribe",
                                    "fields.service-code",
                                    "fields.ke",
                                    "fields.service-name",
                                    "fields.marketing-name",
                                    "fields.distrib-link",
                                    "actions"

                                ]

                                bat = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                quux = set(visible_columns_release)

                                if (bat - quux) or (quux - bat) or \
                                        settings['payloads'][0]['currentState']['pageSize'] != 100:
                                    settings['payloads'][0]['currentState']['pageSize'] = 100
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visible_columns_release
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

                            elif projects['type'] == 'release':
                                print('######' * 100, '\nTHIS BLOCK IS WORKING\n', '######' * 100)
                                payloads_release = [
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
                                                "fields.platform-path",
                                                "fields.tribe",
                                                "fields.service-code",
                                                "fields.ke",
                                                "fields.service-name",
                                                "fields.marketing-name",
                                                "fields.distrib-link",
                                                "actions"
                                            ]
                                        }
                                    }
                                ]
                                settings['payloads'] = payloads_release

                            update_view_settings = users_settings.update_one({"_id": settings['_id']},
                                                                             {"$set": settings})
                            print(update_view_settings.raw_result)

                if f'framework-object-type-{cmdb_type}' not in map(lambda x: x['resource'], view_settings):
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
                        view_settings_for_create.append(settings_view_os)

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
                        view_settings_for_create.append(settings_view_vm)

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
                        view_settings_for_create.append(settings_view_label)

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
                        view_settings_for_create.append(settings_view_version)

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
                        view_settings_for_create.append(settings_view_vcd)


                    elif projects['type'] == 'release':

                        settings_view_release: dict = {
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
                                            "fields.platform-path",
                                            "fields.tribe",
                                            "fields.service-code",
                                            "fields.ke",
                                            "fields.service-name",
                                            "fields.marketing-name",
                                            "fields.distrib-link",
                                            "actions"
                                        ]
                                    }
                                }
                            ]
                        }
                        # users_settings = max(filter(lambda x: x['name'] == 'management.users.settings', collection))
                        settings_view_release['resource'] = f"framework-object-type-{cmdb_type}"
                        settings_view_release['user_id'] = user_id
                        view_settings_for_create.append(settings_view_release)

            if view_settings_for_create:
                create_view_settings = users_settings.insert_many(view_settings_for_create)
                for new_object in create_view_settings.inserted_ids:
                    print(f'Create new settings {new_object} for user {user_id}')

        create_settings(cmdb_projects_vm)
        create_settings(cmdb_projects_os)
        create_settings(cmdb_projects_label)
        create_settings(cmdb_projects_version)
        create_settings(cmdb_projects_vdc)
        create_settings(cmdb_projects_release)


if __name__ == '__main__':
    visible_settings()
