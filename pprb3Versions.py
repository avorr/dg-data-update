#!/usr/bin/python3

import json
import time
import socket
import requests
from functools import reduce
from datetime import datetime
# from pymongo import MongoClient
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from env import portal_info
from vm_passport import cmdb_api
# from vm_passport import objects
from vm_passport import category_id
from vm_passport import get_dg_token
from vm_passport import get_all_jsons
from vm_passport import get_mongodb_objects

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from tools import *


# def json_read(json_object: dict):
#     print(json.dumps(json_object, indent=4))

# def write_to_file(object: str):
#     separator: int = object.index('=')
#     with open('%s.py' % object[:separator], 'w') as file:
#         file.write('%s = %s' % (object[:separator], object[(separator + 1):]))


# def pprb3_versions(portal_name: str, clusters: tuple = (), all_objects: tuple = ()) -> None:
def pprb3_versions(portal_name: str, all_objects: tuple = ()) -> None:
    """main func for autocomplete labels in DataGerry"""

    def create_object(version_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
                      template: bool = False) -> dict:
        if method == 'PUT':
            return cmdb_api(method, f'object/{version_info["public_id"]}', cmdb_token, version_info)
            # print(f'object/{version_info["public_id"]}')

        def get_version(version_info: dict) -> str:
            # if 'nginx_version' in version_info:
            #     return version_info['nginx_version']
            # if 'pgsqlse_version' in version_info:
            #     return version_info['pgsqlse_version']
            # if 'kafka_version' in version_info:
            #     return version_info['kafka_version']
            # if 'version' in version_info:
            # print(next(iter(version_info['version'])))
            if next(iter(version_info['version'])) == 'ERROR':
                return version_info['version']['ERROR']
            if next(iter(version_info['version'])) == 'deployment':
                # print('\n'.join(version_info['version']['deployment'].keys()), version_info['version']['product-version'], version_info['version']['release-version'], sep='\n')
                # print(version_info['version']['product-version'], version_info['version']['release-version'])
                # print(version_info['version'])
                # print('\n'.join(('\n'.join(version_info['version']['deployment'].keys()), version_info['version']['product-version'], version_info['version']['release-version'])))
                # print('##########')
                # return version_info['version']['deployment']
                if not version_info['version']['deployment']:
                    return '\n'.join((version_info['version']['product-version'],
                                      version_info['version']['release-version']))

                return '\n'.join(('\n'.join(version_info['version']['deployment'].keys()),
                                  version_info['version']['product-version'],
                                  version_info['version']['release-version']))

            return version_info['version']

            # else:
            #     return None

        pprb3_object_template: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "name",
                    "value": version_info['service_name']
                },
                {
                    "name": "vm-name",
                    "value": version_info['name']
                },
                {
                    "name": "local-ip",
                    "value": version_info['ip']

                },
                {
                    "name": "tag",
                    "value": version_info['tag']
                },
                {
                    "name": "version",
                    "value": get_version(version_info)
                },
                {
                    "name": "vm-id",
                    "value": version_info['id']
                }
            ]
        }

        if template:
            return pprb3_object_template

        return cmdb_api('POST', 'object/', cmdb_token, pprb3_object_template)

    cmdb_token, user_id = get_dg_token()
    all_categories: tuple = get_mongodb_objects('framework.categories')

    os_passports_category_id = category_id('pprb3-app-versions', 'Pprb3 App Versions',
                                           'fas fa-server', cmdb_token, all_categories)

    os_portal_category_id = \
        category_id(f'Pprb3-Versions-{portal_name}', f'Pprb3-Versions-{portal_name}', 'far fa-folder-open',
                    cmdb_token, all_categories, os_passports_category_id['public_id'])

    all_pprb3_verions: dict = json.loads(requests.request("GET", portal_info[portal_name]['pprb3_versions']).content)

    # for i in all_pprb3_verions['info']:
    #     if i['modules_version']:
    #         for k in i['modules_version']:
    #             print(k.keys())
    # return

    # clusters = map(lambda x: x['metric']['cluster'], cluster_info['data']['result'])
    # allLabels = getOsLabels(clusters)
    # print(allLabels)
    # return
    # from allLabels import allLabels
    # start = time.time()
    # cmdb_projects = get_all_jsons('types', cmdb_token)

    cmdb_projects: tuple = get_mongodb_objects('framework.types')

    # for stand in all_pprb3_verions['info']:
    #     if not any(map(lambda x: any(map(lambda y: y['name'] == f"pprb3-versions-{portal_name}--{stand['project_id']}",
    #                                      x['results'])), cmdb_projects)) and stand['modules_version']:
    #         print(stand)

    # for stand in all_pprb3_verions['info']:
    #     if not any(map(lambda x: any(map(lambda y: y['name'] == f"pprb3-versions-{portal_name}--{stand['project_id']}",
    #                                      x['results'])), cmdb_projects)) and stand['modules_version']:
    # and stand['project_name'] == 'gt-dvp-dev-admin-platform':

    for stand in all_pprb3_verions['info']:
        if not any(map(lambda y: y['name'] == f"pprb3-versions-{portal_name}--{stand['project_id']}", cmdb_projects)) \
                and stand['modules_version']:  # and stand['project_name'] == 'gt-business-test-platform':

            payload_type_template: dict = {
                "fields": [
                    {
                        "type": "text",
                        "name": "name",
                        "label": "name"
                    },
                    {
                        "type": "text",
                        "name": "vm-name",
                        "label": "vm name"
                    },
                    {
                        "type": "text",
                        "name": "local-ip",
                        "label": "local ip"
                    },
                    {
                        "type": "text",
                        "name": "tag",
                        "label": "tag"
                    },
                    {
                        "type": "text",
                        "name": "version",
                        "label": "version"
                    },
                    {
                        "type": "text",
                        "name": "vm-id",
                        "label": "vm id"
                    }
                ],
                "active": True,
                "version": "1.0.0",
                "author_id": user_id,
                "render_meta": {
                    "icon": "fab fa-centos",
                    "sections": [
                        {
                            "fields": [
                                "name",
                                "vm-name",
                                "local-ip",
                                "tag",
                                "version",
                                "vm-id"
                            ],
                            "type": "section",
                            "name": f"pprb3-versions-{portal_name}--{stand['project_id']}",
                            "label": stand['project_id']
                        }
                    ],
                    "externals": [],
                    "summary": {
                        "fields": [
                            "name",
                            "vm-name",
                            "local-ip",
                            "tag",
                            "version"
                        ]
                    }
                },
                "acl": {
                    "activated": True,
                    "groups": {
                        "includes": {
                            "1": [
                                "CREATE",
                                "READ",
                                "UPDATE",
                                "DELETE"
                            ],
                            "2": [
                                "READ"
                            ]
                        }
                    }
                },
                "name": f"pprb3-versions-{portal_name}--{stand['project_id']}",
                "label": stand['project_name'],
                "description": f'pprb3 versions {stand["project_id"]}'
            }

            create_type = cmdb_api('POST', 'types/', cmdb_token, payload_type_template)
            print(create_type)
            print(create_type['result_id'], 'new type id')

            data_cat_template: dict = {
                "public_id": os_portal_category_id['public_id'],
                "name": os_portal_category_id['name'],
                "label": os_portal_category_id['label'],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": os_passports_category_id['public_id'],
                "types": os_portal_category_id['types']
            }

            if not create_type['result_id']:
                return
            data_cat_template['types'].append(create_type['result_id'])
            put_type_in_category = \
                cmdb_api('PUT', f"categories/{os_portal_category_id['public_id']}", cmdb_token, data_cat_template)

            print('PUT TYPE IN CATEGORY', put_type_in_category)
            print('DATA CATEGORY TEMPLATE', data_cat_template)

            for version in stand['modules_version']:
                create_pprb3_version_object = create_object(version, cmdb_token, create_type['result_id'], user_id)
                print('CREATE OBJECT', create_pprb3_version_object)
                time.sleep(0.1)

    all_objects: tuple = get_mongodb_objects('framework.objects')
    # from vm_passport import get_mongodb_objects
    # cmdb_projects = get_all_jsons('types', cmdb_token)
    # cmdb_projects: tuple = get_mongodb_objects('framework.types')

    all_pprb3_types = tuple(filter(lambda x: f'pprb3-versions-{portal_name}--' in x['name'], cmdb_projects))

    # for pprb3_type in all_pprb3_types:
    #     for pprb3_verions in all_pprb3_verions['info']:
    #         if pprb3_type['name'][21:] == pprb3_verions['project_id']:
    #             print(pprb3_verions['project_id'])

    # all_pprb3_types = reduce(lambda x, y: x + y, map(lambda foo: tuple(
    #     filter(lambda bar: f'pprb3-versions-{portal_name}--' in bar['name'], foo['results'])), cmdb_projects))

    # return
    for pprb3_type in all_pprb3_types:
        for pprb3_verions in all_pprb3_verions['info']:
            if pprb3_type['name'][21:] == pprb3_verions['project_id'] and pprb3_verions['modules_version']:
                # and pprb3_type['name'][21:] == 'fe6d283e-c96e-4b32-b1b7-72c004066f4e':

                # if pprb3_type['name'][21:] == pprb3_verions['project_id'] and pprb3_verions['modules_version'] != None:

                dg_pprb3_objects = tuple(filter(lambda x: x['type_id'] == pprb3_type['public_id'], all_objects))

                # foo = map(lambda x: '%s--%s' % (x['fields'][3]['value'], x['fields'][5]['value']), dg_pprb3_objects)
                for pprb3_module in pprb3_verions['modules_version']:
                    for dg_object in dg_pprb3_objects:
                        pprb3_object_tmp: dict = \
                            create_object(pprb3_module, cmdb_token, pprb3_type['public_id'], user_id, template=True)
                        if pprb3_module['id'] == dg_object['fields'][5]['value'] and \
                                pprb3_module['tag'] == dg_object['fields'][3]['value'] and \
                                pprb3_object_tmp['fields'] != dg_object['fields']:

                            update_object_template: dict = {
                                "type_id": dg_object['type_id'],
                                "status": dg_object['status'],
                                "version": dg_object['version'],
                                "creation_time": {
                                    # "$date": int(datetime.datetime.timestamp(dg_object['creation_time']) * 1000)
                                    "$date": int(time.mktime(dg_object['creation_time'].timetuple()) * 1000)
                                },
                                "author_id": dg_object['author_id'],
                                "last_edit_time": {
                                    "$date": int(time.time() * 1000)
                                },
                                "editor_id": user_id,
                                "active": dg_object["active"],
                                "fields": pprb3_object_tmp['fields'],
                                "public_id": dg_object['public_id'],
                                "views": dg_object["views"],
                                "comment": ""
                            }
                            create_object(update_object_template, cmdb_token, pprb3_type['public_id'], user_id, 'PUT')
                            print(f"UPDATE PPRB3 VERSION IN  {dg_object['type_id']} TYPE")

                        # if pprb3_module['id'] == dg_object['fields'][5]['value'] and \
                        #         pprb3_module['tag'] == dg_object['fields'][3]['value']:
                    if '%s--%s' % (pprb3_module['tag'], pprb3_module['id']) not in \
                            map(lambda x: '%s--%s' % (x['fields'][3]['value'], x['fields'][5]['value']),
                                dg_pprb3_objects):
                        print('CREATE PPRB3 VERSION in %s' % pprb3_type['public_id'])
                        create_object(pprb3_module, cmdb_token, pprb3_type['public_id'], user_id)
                        time.sleep(0.1)

                for dg_object in dg_pprb3_objects:
                    if '%s--%s' % (dg_object['fields'][3]['value'], dg_object['fields'][5]['value']) not in \
                            map(lambda x: '%s--%s' % (x['tag'], x['id']), pprb3_verions['modules_version']):
                        print('DELETE PPRB3 VERSION %s--%s' % (dg_object['fields'][3]['value'],
                                                               dg_object['fields'][5]['value']))
                        cmdb_api('DELETE', f"object/{dg_object['public_id']}", cmdb_token)
                        time.sleep(0.1)


if __name__ == '__main__':
    pprb3_versions(next(iter(portal_info)))


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
    """function for checking resolving dns names"""
    try:
        socket.gethostbyname(dns_name)
        return True
    except socket.error as Error:
        print(dns_name, Error)
        return False
