#!/usr/local/bin/python3

import time
from tools import *
from pymongo import MongoClient
from common_function import get_mongodb_objects


def visible_settings() -> None:
    """
    Main func for creating visible settings in cmdb
    :return: None
    """
    cmdb_projects: tuple = get_mongodb_objects("framework.types")

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

    for dg_type in cmdb_projects:
        if dg_type["name"] != "Release-Artifact":
            if dg_type['render_meta']['sections'][0]['fields'][2] == 'os-type':
                cmdb_projects_vm['items'].append(dg_type['public_id'])
            elif dg_type['render_meta']['sections'][0]['fields'][1] == 'limits.cpu-hard':
                cmdb_projects_os['items'].append(dg_type['public_id'])
            elif dg_type['render_meta']['sections'][0]['fields'][3] == 'SUBSYSTEM':
                cmdb_projects_label['items'].append(dg_type['public_id'])
            elif dg_type['render_meta']['sections'][0]['fields'][4] == 'version':
                cmdb_projects_version['items'].append(dg_type['public_id'])
            elif dg_type['render_meta']['sections'][0]['fields'][1] == 'datacenter-name':
                cmdb_projects_vdc['items'].append(dg_type['public_id'])
            elif dg_type['render_meta']['sections'][0]['fields'][0] == 'platform-path':
                cmdb_projects_release['items'].append(dg_type['public_id'])

    cmdb_users: tuple = get_mongodb_objects("management.users")
    cmdb_users = tuple(map(lambda x: x["public_id"], cmdb_users))

    from env import mongo_db_url
    cluster = MongoClient(mongo_db_url)
    db = cluster['cmdb']

    for user_id in cmdb_users:

        users_settings = db.get_collection('management.users.settings')
        display_settings = users_settings.find(
            {
                'user_id': user_id
            }
        )

        # display_settings = get_mongodb_objects('management.users.settings', {'user_id': user_id})

        view_settings = list()
        for settings in display_settings:
            view_settings.append(settings)
        del display_settings

        def create_settings(projects: list) -> None:
            view_settings_for_create = list()
            for cmdb_type in projects["items"]:
                for settings in view_settings:

                    if "framework-object-type-%s" % cmdb_type == settings["resource"]:
                        if "currentState" in settings["payloads"][0]:
                            if "fields.additional-disk" in settings["payloads"][0]["currentState"]["visibleColumns"]:

                                visible_columns_vm: list = [
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

                                if (foo - bar) or (bar - foo) or \
                                        settings['payloads'][0]['currentState']['pageSize'] != 200:
                                    settings['payloads'][0]['currentState']['pageSize'] = 200
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visible_columns_vm
                                    update_view_settings = users_settings.update_one(
                                        {
                                            "_id": settings['_id']
                                        },
                                        {
                                            "$set": settings
                                        }
                                    )
                                    print(update_view_settings.raw_result)
                                    time.sleep(0.5)

                            elif 'fields.limits.cpu-hard' in settings['payloads'][0]['currentState']["visibleColumns"]:

                                visible_columns_os: list = [
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
                                    update_view_settings = users_settings.update_one(
                                        {
                                            "_id": settings['_id']
                                        },
                                        {
                                            "$set": settings
                                        }
                                    )
                                    print(update_view_settings.raw_result)
                                del baz, zip

                            elif 'fields.SUBSYSTEM' in settings['payloads'][0]['currentState']["visibleColumns"]:

                                visible_columns_label: list = [
                                    'fields.namespace',
                                    'fields.name',
                                    'fields.app',
                                    'fields.SUBSYSTEM',
                                    'fields.deployment',
                                    'fields.deploymentconfig',
                                    'fields.deployDate',
                                    'fields.distribVersion',
                                    'fields.version',
                                    'fields.build',
                                    'fields.image',
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
                                    update_view_settings = users_settings.update_one(
                                        {
                                            "_id": settings['_id']
                                        },
                                        {
                                            "$set": settings
                                        }
                                    )
                                    print(update_view_settings.raw_result)
                                del bat, quux


                            elif 'fields.datacenter-name' in settings['payloads'][0]['currentState']["visibleColumns"]:

                                visible_columns_vcd: list = [
                                    'fields.name',
                                    'fields.datacenter-name',
                                    'fields.networks',
                                    'fields.dns-nameservers',
                                    'fields.domain',
                                    'fields.group',
                                    'actions'
                                ]

                                bat = set(settings['payloads'][0]['currentState']["visibleColumns"])
                                quux = set(visible_columns_vcd)

                                if (bat - quux) or (quux - bat) or \
                                        settings['payloads'][0]['currentState']['pageSize'] != 100:
                                    settings['payloads'][0]['currentState']['pageSize'] = 100
                                    settings['payloads'][0]['currentState']["visibleColumns"] = visible_columns_vcd
                                    update_view_settings = users_settings.update_one(
                                        {
                                            "_id": settings['_id']
                                        },
                                        {
                                            "$set": settings
                                        }
                                    )
                                    print(update_view_settings.raw_result)
                                del bat, quux

                            elif 'fields.tag' in settings['payloads'][0]['currentState']["visibleColumns"]:

                                visible_columns_version: list = [
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
                                    update_view_settings = users_settings.update_one(
                                        {
                                            "_id": settings['_id']
                                        },
                                        {
                                            "$set": settings
                                        }
                                    )
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
                                    update_view_settings = users_settings.update_one(
                                        {
                                            "_id": settings['_id']
                                        },
                                        {
                                            "$set": settings
                                        }
                                    )
                                    print(update_view_settings.raw_result)
                                del bat, quux


                        else:
                            if projects['type'] == 'vm':
                                print('######' * 100, '\nTHIS BLOCK IS WORKING\n', '######' * 100)
                                payloads_vm: list = [
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
                                payloads_os: list = [
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
                                payloads_label: list = [
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
                                                'fields.build',
                                                'fields.image',
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
                                payloads_version: list = [
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
                                payloads_vcd: list = [
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
                                                'fields.domain',
                                                'fields.group',
                                                'actions'
                                            ]
                                        }
                                    }
                                ]
                                settings['payloads'] = payloads_vcd

                            elif projects['type'] == 'release':
                                print('######' * 100, '\nTHIS BLOCK IS WORKING\n', '######' * 100)
                                payloads_release: list = [
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

                            update_view_settings = users_settings.update_one(
                                {
                                    "_id": settings['_id']
                                },
                                {
                                    "$set": settings
                                })
                            print(update_view_settings.raw_result)

                if 'framework-object-type-%s' % cmdb_type not in map(lambda x: x['resource'], view_settings):
                    if projects['type'] == 'os':
                        settings_view_os: dict = {
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

                        settings_view_os['resource'] = "framework-object-type-%s" % cmdb_type
                        settings_view_os['user_id'] = user_id
                        view_settings_for_create.append(settings_view_os)

                    elif projects['type'] == 'vm':
                        settings_view_vm: dict = \
                            {
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

                        settings_view_vm['resource'] = "framework-object-type-%s" % cmdb_type
                        settings_view_vm['user_id'] = user_id
                        view_settings_for_create.append(settings_view_vm)

                    elif projects['type'] == 'label':

                        settings_view_label: dict = \
                            {
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
                                                "fields.build",
                                                "fields.image",
                                                "fields.security.istio.io/tlsMode",
                                                "fields.jenkinsDeployUser",
                                                "actions"
                                            ]
                                        }
                                    }
                                ]
                            }

                        # users_settings = max(filter(lambda x: x['name'] == 'management.users.settings', collection))

                        settings_view_label['resource'] = "framework-object-type-%s" % cmdb_type
                        settings_view_label['user_id'] = user_id
                        view_settings_for_create.append(settings_view_label)

                    elif projects['type'] == 'version':
                        settings_view_version: dict = \
                            {
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
                        settings_view_version['resource'] = "framework-object-type-%s" % cmdb_type
                        settings_view_version['user_id'] = user_id
                        view_settings_for_create.append(settings_view_version)

                    elif projects['type'] == 'vcd':

                        settings_view_vcd: dict = \
                            {
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
                                                "fields.domain",
                                                "fields.group",
                                                "actions"
                                            ]
                                        }
                                    }
                                ]
                            }
                        # users_settings = max(filter(lambda x: x['name'] == 'management.users.settings', collection))
                        settings_view_vcd['resource'] = "framework-object-type-%s" % cmdb_type
                        settings_view_vcd['user_id'] = user_id
                        view_settings_for_create.append(settings_view_vcd)


                    elif projects['type'] == 'release':

                        settings_view_release: dict = \
                            {
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
                        settings_view_release['resource'] = "framework-object-type-%s" % cmdb_type
                        settings_view_release['user_id'] = user_id
                        view_settings_for_create.append(settings_view_release)

            if view_settings_for_create:
                create_view_settings = users_settings.insert_many(view_settings_for_create)
                for new_object in create_view_settings.inserted_ids:
                    print('Create new settings %s for user %s' % (new_object, user_id))

        create_settings(cmdb_projects_vm)
        create_settings(cmdb_projects_os)
        create_settings(cmdb_projects_label)
        create_settings(cmdb_projects_version)
        create_settings(cmdb_projects_vdc)
        create_settings(cmdb_projects_release)


if __name__ == '__main__':
    visible_settings()
