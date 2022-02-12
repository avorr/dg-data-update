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
from vm_passport import getCmdbToken
from vm_passport import getInfoFromAllPage

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from tools import *
# def json_read(json_object: dict):
#     print(json.dumps(json_object, indent=4))

# def write_to_file(object: str):
#     separator: int = object.index('=')
#     with open('%s.py' % object[:separator], 'w') as file:
#         file.write('%s = %s' % (object[:separator], object[(separator + 1):]))


# def pprb3Versions(portal_name: str, clusters: tuple = (), all_objects: tuple = ()) -> None:
def pprb3Versions(portal_name: str, all_objects: tuple = ()) -> None:
    """main func for autocomplete labels in DataGerry"""

    def CreateObject(versionInfo: dict, cmdbToken: str, type_id: str, author_id: int, method: str = 'POST',
                     template: bool = False) -> dict:
        if method == 'PUT':
            # return cmdb_api(method, f'object/{versionInfo["public_id"]}', cmdbToken, versionInfo)
            print(f'object/{versionInfo["public_id"]}')

        def getLabel(labels: dict, label: str) -> str:
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

        def getVersion(versionInfo: dict) -> str:
            if 'nginx_version' in versionInfo:
                return versionInfo['nginx_version']
            if 'pgse_version' in versionInfo:
                return versionInfo['pgse_version']
            if 'kafka_version' in versionInfo:
                return versionInfo['kafka_version']
            if 'wf_info' in versionInfo:
                # print(next(iter(versionInfo['wf_info'])))
                if next(iter(versionInfo['wf_info'])) == 'ERROR':
                    return versionInfo['wf_info']['ERROR']
                if next(iter(versionInfo['wf_info'])) == 'deployment':
                    # print('\n'.join(versionInfo['wf_info']['deployment'].keys()), versionInfo['wf_info']['product-version'], versionInfo['wf_info']['release-version'], sep='\n')
                    # print(versionInfo['wf_info']['product-version'], versionInfo['wf_info']['release-version'])
                    # print(versionInfo['wf_info'])
                    # print('\n'.join(('\n'.join(versionInfo['wf_info']['deployment'].keys()), versionInfo['wf_info']['product-version'], versionInfo['wf_info']['release-version'])))
                    # print('##########')
                    # return versionInfo['wf_info']['deployment']
                    return '\n'.join(('\n'.join(versionInfo['wf_info']['deployment'].keys()), versionInfo['wf_info']['product-version'], versionInfo['wf_info']['release-version']))

                return versionInfo['wf_info']

            else:
                return None


        labelObjectTemplate: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "name",
                    "value": versionInfo['service_name']
                },
                {
                    "name": "vm-name",
                    "value": versionInfo['name']
                },
                {
                    "name": "local-ip",
                    "value": versionInfo['ip']

                },
                {
                    "name": "tag",
                    "value": versionInfo['tag']
                },
                {
                    "name": "version",
                    "value": getVersion(versionInfo)
                }
            ]
        }

        # json_read(labelObjectTemplate)

        if template:
            return labelObjectTemplate

        return cmdb_api('POST', 'object/', cmdbToken, labelObjectTemplate)

    cmdbToken, userId = getCmdbToken()
    all_categories = getInfoFromAllPage('categories', cmdbToken)

    os_passports_category_id = category_id('pprb3-app-versions', 'Pprb3 App Versions', 'fas fa-server', cmdbToken,
                                             all_categories)

    os_portal_category_id = \
        category_id(f'Pprb3-Versions-{portal_name}', f'Pprb3-Versions-{portal_name}', 'far fa-folder-open',
                     cmdbToken, all_categories,
                     os_passports_category_id['public_id'])


    def check_resolves(dnsName: str) -> bool:
        """function for checking resolving dns names"""
        try:
            socket.gethostbyname(dnsName)
            return True
        except socket.error as Error:
            print(dnsName, Error)
            return False

    allPprb3Verions: dict = json.loads(requests.request("GET", portal_info[portal_name]['pprb3_versions']).content)

    # for i in allPprb3Verions['info']:
    #     if i['modules_version']:
    #         for k in i['modules_version']:
    #             print(k.keys())
    # return

    # clusters = map(lambda x: x['metric']['cluster'], cluster_info['data']['result'])
    # allLabels = getOsLabels(clusters)
    # print(allLabels)
    # return
    # from allLabels import allLabels

    cmdb_projects = getInfoFromAllPage('types', cmdbToken)
    # write_to_file(f"{cmdb_projects=}")
    # from cmdb_projects import cmdb_projects

    # for stand in allPprb3Verions['info']:
    #     if not any(map(lambda x: any(map(lambda y: y['name'] == f"pprb3-versions-{portal_name}--{stand['project_id']}",
    #                                      x['results'])), cmdb_projects)) and stand['modules_version']:
    #         print(stand)

    for stand in allPprb3Verions['info']:
        if not any(map(lambda x: any(map(lambda y: y['name'] == f"pprb3-versions-{portal_name}--{stand['project_id']}",
                                         x['results'])), cmdb_projects)) and stand['modules_version']:
                # and stand['project_name'] == 'gt-dvp-dev-admin-platform':
            data_type_template: dict = {
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
                "author_id": userId,
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
            create_type = cmdb_api('POST', 'types/', cmdbToken, data_type_template)
            print(create_type)

            # all_types_pages = getInfoFromAllPage('types', cmdbToken)[0]['pager']['total_pages']

            # new_all_types_pages = list()
            # for page in range(1, all_types_pages + 1):
            #     response_page = cmdb_api('GET', f'types/?page={page}', cmdbToken)
            #     new_all_types_pages.append(response_page)

            # newTypeId = None
            # for new_types in new_all_types_pages:
            #     for new_item in new_types['results']:
            #         if new_item['name'] == f"pprb3-versions-{portal_name}--{stand['project_id']}":
            #             newTypeId = new_item['public_id']
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

            if create_type['result_id'] == None:
                return
            data_cat_template['types'].append(create_type['result_id'])
            put_type_in_catigories = cmdb_api('PUT', f"categories/{os_portal_category_id['public_id']}", cmdbToken,
                                              data_cat_template)

            print('PUT TYPE IN CATIGORIES', put_type_in_catigories)
            print('DATA CATATEGORIE TEMPLATE', data_cat_template)

            # create_type['result_id'] = 120
            for version in stand['modules_version']:
                create_object = CreateObject(version, cmdbToken, create_type['result_id'], userId)
                print('CREATE OBJECT', create_object)
                time.sleep(0.1)


    from vm_passport import get_mongodb_objects
    all_objects = get_mongodb_objects('framework.objects')

    cmdb_projects = getInfoFromAllPage('types', cmdbToken)

    allTypesVersions = reduce(lambda x, y: x + y, map(lambda foo: tuple(
        filter(lambda bar: f'pprb3-versions-{portal_name}--' in bar['name'], foo['results'])), cmdb_projects))


    return
    for cmdbTypeVersion in allTypesVersions:
        for projectsPprb3Verions in allPprb3Verions:
            
            if cmdbTypeVersion['label'] == projectsPprb3Verions['cluster']:
                cmdb_namespaces = tuple(filter(lambda x: x['type_id'] == cmdb_cluster['public_id'], all_objects))
                for os_namespace in cluster['info']:
                    if os_namespace['namespace'] not in map(lambda x: x.get('fields')[0]['value'], cmdb_namespaces):
                        print('NAMESPACE FOR CREATE', os_namespace['namespace'])
                        # objects(os_namespace, cmdbToken, cmdb_cluster['public_id'], userId, 'NAMESPACE')
                        time.sleep(0.1)

                    for cmdb_ns in cmdb_namespaces:
                        ns_template = objects(os_namespace, cmdbToken, cmdb_cluster['public_id'], userId,
                                              'NAMESPACE', template=True)
                        if cmdb_ns['fields'][0]['value'] == os_namespace['namespace'] and cmdb_ns['fields'] != \
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
                                "editor_id": userId,
                                "active": True,
                                "fields": ns_template['fields'],
                                "public_id": cmdb_ns['public_id'],
                                "views": 0,
                                "comment": ""
                            }

                            time.sleep(0.1)
                            print(f"UPDATE NAMESPACE in {cmdb_ns['type_id']}", os_namespace['namespace'])
                            objects(updateObjectTemplate, cmdbToken, cmdb_cluster['public_id'], userId, 'PUT')

                for cmdb_ns in cmdb_namespaces:
                    if cmdb_ns['fields'][0]['value'] not in map(lambda x: x['namespace'], cluster['info']):
                        print('DELETE NAMESPACE', cmdb_ns['fields'][0]['value'])
                        cmdb_api('DELETE', f"object/{cmdb_ns['public_id']}", cmdbToken)
                        time.sleep(0.1)




if __name__ == '__main__':
    pprb3Versions(next(iter(portal_info)))



# for cmdb_cluster in allTypesLabels:
#     for cluster in allLabels:
#         if cmdb_cluster['label'] == cluster['cluster']:
#             cmdb_namespaces = tuple(filter(lambda x: x['type_id'] == cmdb_cluster['public_id'], all_objects))
#
#             for podInfo in cluster['labels']:
#                 template = CreateObject(podInfo, cmdbToken, cmdb_cluster['public_id'], userId, template=True)
#                 if template['fields'] not in map(lambda x: x.get('fields'), cmdb_namespaces):
#                     createLabel = CreateObject(podInfo, cmdbToken, cmdb_cluster['public_id'], userId)
#                     print('CREATE LABEL <--->', template['fields'][1]['value'], createLabel)
#                     time.sleep(0.1)
#
#             for cmdbLabel in cmdb_namespaces:
#                 if cmdbLabel['fields'][1]['value'] not in map(lambda x: x['name'], cluster['labels']):
#                     print('DELETE LABEL <--->', cmdbLabel['fields'][1]['value'])
#                     cmdb_api('DELETE', f"object/{cmdbLabel['public_id']}", cmdbToken)
#                     time.sleep(0.1)
