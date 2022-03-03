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
            # return cmdb_api(method, f'object/{version_info["public_id"]}', cmdb_token, version_info)
            print(f'object/{version_info["public_id"]}')

        def get_version(version_info: dict) -> str:
            if 'nginx_version' in version_info:
                return version_info['nginx_version']
            if 'pgsqlse_version' in version_info:
                return version_info['pgsqlse_version']
            if 'kafka_version' in version_info:
                return version_info['kafka_version']
            if 'wf_info' in version_info:
                # print(next(iter(version_info['wf_info'])))
                if next(iter(version_info['wf_info'])) == 'ERROR':
                    return version_info['wf_info']['ERROR']
                if next(iter(version_info['wf_info'])) == 'deployment':
                    # print('\n'.join(version_info['wf_info']['deployment'].keys()), version_info['wf_info']['product-version'], version_info['wf_info']['release-version'], sep='\n')
                    # print(version_info['wf_info']['product-version'], version_info['wf_info']['release-version'])
                    # print(version_info['wf_info'])
                    # print('\n'.join(('\n'.join(version_info['wf_info']['deployment'].keys()), version_info['wf_info']['product-version'], version_info['wf_info']['release-version'])))
                    # print('##########')
                    # return version_info['wf_info']['deployment']
                    if not version_info['wf_info']['deployment']:
                        return '\n'.join((version_info['wf_info']['product-version'],
                                          version_info['wf_info']['release-version']))

                    return '\n'.join(('\n'.join(version_info['wf_info']['deployment'].keys()),
                                      version_info['wf_info']['product-version'],
                                      version_info['wf_info']['release-version']))

                return version_info['wf_info']

            else:
                return None

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
                }
            ]
        }

        if template:
            return pprb3_object_template

        return cmdb_api('POST', 'object/', cmdb_token, pprb3_object_template)

    cmdb_token, user_id = get_dg_token()
    all_categories = get_all_jsons('categories', cmdb_token)

    os_passports_category_id = category_id('pprb3-app-versions', 'Pprb3 App Versions', 'fas fa-server', cmdb_token,
                                           all_categories)

    os_portal_category_id = \
        category_id(f'Pprb3-Versions-{portal_name}', f'Pprb3-Versions-{portal_name}', 'far fa-folder-open',
                    cmdb_token, all_categories,
                    os_passports_category_id['public_id'])

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

    from vm_passport import get_mongodb_objects
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
                                "version"
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
                # create_pprb3_version_object = create_object(version, cmdb_token, 190, user_id)
                print('CREATE OBJECT', create_pprb3_version_object)
                time.sleep(0.1)

    # return
    all_objects: tuple = get_mongodb_objects('framework.objects')
    # from vm_passport import get_mongodb_objects
    # cmdb_projects = get_all_jsons('types', cmdb_token)
    # cmdb_projects: tuple = get_mongodb_objects('framework.types')

    all_pprb3_types = tuple(filter(lambda x: f'pprb3-versions-{portal_name}--' in x['name'], cmdb_projects))
    # print(all_pprb3_types)

    # for i in all_pprb3_types:
    #     print(i['name'][21:])
    #     print(i['label'])
    # for pprb3_verions in all_pprb3_verions['info']:
    #     print(pprb3_verions['project_id'])

    # for pprb3_type in all_pprb3_types:
    #     for pprb3_verions in all_pprb3_verions['info']:
    #         if pprb3_type['name'][21:] == pprb3_verions['project_id']:
    #             print(pprb3_verions['project_id'])

    # all_pprb3_types = reduce(lambda x, y: x + y, map(lambda foo: tuple(
    #     filter(lambda bar: f'pprb3-versions-{portal_name}--' in bar['name'], foo['results'])), cmdb_projects))
    # print(all_pprb3_types)

    # for i in all_pprb3_types:
    #     print(i)

    return
    for pprb3_type in all_pprb3_types:
        for pprb3_verions in all_pprb3_verions['info']:
            if pprb3_type['name'][21:] == pprb3_verions['project_id'] and pprb3_type['name'][21:] == \
                    'fe6d283e-c96e-4b32-b1b7-72c004066f4e' and pprb3_verions['modules_version']:
            # if pprb3_type['name'][21:] == pprb3_verions['project_id'] and pprb3_verions['modules_version'] != None:

                # print()
                # print(pprb3_verions['modules_version'])
                # print(pprb3_type['name'][21:])
                # print(pprb3_verions['project_id'])

                # if pprb3_type['label'] == pprb3_verions['cluster']:
                dg_pprb3_objects = tuple(filter(lambda x: x['type_id'] == pprb3_type['public_id'], all_objects))

                # for i in dg_pprb3_objects:
                #     print(i)
                # return
                for pprb3_module in pprb3_verions['modules_version']:
                    print(pprb3_module)


                return
                for ve_pprb3_object in all_pprb3_verions['info']:
                    print(ve_pprb3_object)
                    return
                    if ve_pprb3_object['namespace'] not in map(lambda x: x.get('fields')[0]['value'], dg_pprb3_objects):
                        print('NAMESPACE FOR CREATE', ve_pprb3_object['namespace'])
                        # objects(ve_pprb3_object, cmdb_token, cmdb_cluster['public_id'], user_id, 'NAMESPACE')
                        time.sleep(0.1)

                    for cmdb_ns in dg_pprb3_objects:
                        ns_template = objects(ve_pprb3_object, cmdb_token, cmdb_cluster['public_id'], user_id,
                                              'NAMESPACE', template=True)
                        if cmdb_ns['fields'][0]['value'] == ve_pprb3_object['namespace'] and cmdb_ns['fields'] != \
                                ns_template['fields']:
                            updateObjectTemplate: dict = {
                                "type_id": cmdb_ns['type_id'],
                                "status": True,
                                "version": "1.0.1",
                                "creation_time": {
                                    "$date": int(datetime.datetime.timestamp(cmdb_ns['creation_time']) * 1000)
                                },
                                "author_id": cmdb_ns['author_id'],
                                "last_edit_time": {
                                    "$date": int(time.time() * 1000)
                                },
                                "editor_id": user_id,
                                "active": True,
                                "fields": ns_template['fields'],
                                "public_id": cmdb_ns['public_id'],
                                "views": 0,
                                "comment": ""
                            }

                            time.sleep(0.1)
                            print(f"UPDATE NAMESPACE in {cmdb_ns['type_id']}", ve_pprb3_object['namespace'])
                            objects(updateObjectTemplate, cmdb_token, cmdb_cluster['public_id'], user_id, 'PUT')

                for cmdb_ns in dg_pprb3_objects:
                    if cmdb_ns['fields'][0]['value'] not in map(lambda x: x['namespace'], cluster['info']):
                        print('DELETE NAMESPACE', cmdb_ns['fields'][0]['value'])
                        cmdb_api('DELETE', f"object/{cmdb_ns['public_id']}", cmdb_token)
                        time.sleep(0.1)


if __name__ == '__main__':
    pprb3_versions(next(iter(portal_info)))


# for cmdb_cluster in allTypesLabels:
#     for cluster in allLabels:
#         if cmdb_cluster['label'] == cluster['cluster']:
#             dg_pprb3_objects = tuple(filter(lambda x: x['type_id'] == cmdb_cluster['public_id'], all_objects))
#
#             for podInfo in cluster['labels']:
#                 template = create_object(podInfo, cmdb_token, cmdb_cluster['public_id'], user_id, template=True)
#                 if template['fields'] not in map(lambda x: x.get('fields'), dg_pprb3_objects):
#                     createLabel = create_object(podInfo, cmdb_token, cmdb_cluster['public_id'], user_id)
#                     print('CREATE LABEL <--->', template['fields'][1]['value'], createLabel)
#                     time.sleep(0.1)
#
#             for cmdbLabel in dg_pprb3_objects:
#                 if cmdbLabel['fields'][1]['value'] not in map(lambda x: x['name'], cluster['labels']):
#                     print('DELETE LABEL <--->', cmdbLabel['fields'][1]['value'])
#                     cmdb_api('DELETE', f"object/{cmdbLabel['public_id']}", cmdb_token)
#                     time.sleep(0.1)


#####################################


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
