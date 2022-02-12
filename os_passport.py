#!/usr/bin/python3

import json
import time
import requests
import datetime
from functools import reduce
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from env import portal_info
from vm_passport import cmdb_api
from vm_passport import objects
from vm_passport import category_id
from vm_passport import getCmdbToken
from vm_passport import getInfoFromAllPage

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def json_read(json_object: dict):
    print(json.dumps(json_object, indent=4))


def PassportsOS(portal_name: str, all_objects: tuple) -> None:
    cmdbToken, userId = getCmdbToken()
    all_categories = getInfoFromAllPage('categories', cmdbToken)

    osPassportsCategorieId = category_id('passports-os', 'Passports OpenShift', 'fab fa-redhat', cmdbToken,
                                             all_categories)
    osPortalCategorieId = category_id(f'OS-{portal_name}', f'OS-{portal_name}', 'far fa-folder-open', cmdbToken,
                                          all_categories,
                                          osPassportsCategorieId['public_id'])

    def get_os_info() -> dict:
        return json.loads(requests.request("GET", portal_info[portal_name]['metrics']).content)

    cluster_info = get_os_info()
    clusters = map(lambda x: x['metric']['cluster'], cluster_info['data']['result'])

    os_info = list()
    for cluster in set(clusters):
        metrics = list()
        os_info.append(dict(cluster=cluster, info=metrics))
        for info in cluster_info['data']['result']:
            if cluster == info['metric']['cluster']:
                metrics.append(info['metric']['namespace'])

    for info in os_info:
        info['info'] = list(set(info['info']))
        i = -1
        for namespace in info['info']:
            i += 1
            info['info'][i] = dict(namespace=namespace, info=[])

    for item in os_info:
        for info in item['info']:
            for metric in cluster_info['data']['result']:
                if item['cluster'] == metric['metric']['cluster'] and \
                        info['namespace'] == metric['metric']['namespace']:
                    info['info'].append((metric['metric']['resource'], metric['metric']['type'], metric['value']))

    cmdb_projects = getInfoFromAllPage('types', cmdbToken)

    for cluster in os_info:
        if not any(map(lambda x: any(
                map(lambda y: y['name'] == f"os-cluster-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                    x['results'])),
                       cmdb_projects)):  # and cluster['cluster'] == 'ocp.bootcampsdp.tech':

            data_type_template: dict = {
                "fields": [
                    {
                        "type": "text",
                        "name": "namespace",
                        "label": "namespace"
                    },
                    {
                        "type": "text",
                        "name": "limits.cpu-hard",
                        "label": "limits.cpu-hard"
                    },
                    {
                        "type": "text",
                        "name": "limits.cpu-used",
                        "label": "limits.cpu-used"
                    },
                    {
                        "type": "text",
                        "name": "cores-usage",
                        "label": "cores usage (%)"
                    },
                    {
                        "type": "text",
                        "name": "limits.memory-hard",
                        "label": "limits.memory-hard (Gi)"
                    },
                    {
                        "type": "text",
                        "name": "limits.memory-used",
                        "label": "limits.memory-used (Gi)"
                    },
                    {
                        "type": "text",
                        "name": "memory-usage",
                        "label": "memory usage (%)"
                    }
                ],
                "active": True,
                "version": "1.0.0",
                "author_id": userId,
                "render_meta": {
                    # "icon": "fas fa-clipboard-list",
                    "icon": "fas fa-dharmachakra",
                    "sections": [
                        {
                            "fields": [
                                "namespace",
                                "limits.cpu-hard",
                                "limits.cpu-used",
                                "cores-usage",
                                "limits.memory-hard",
                                "limits.memory-used",
                                "memory-usage"
                            ],
                            "type": "section",
                            "name": f"os-cluster-{portal_name}--{cluster['cluster']}",
                            "label": cluster['cluster']
                        }
                    ],
                    "externals": [],
                    "summary": {
                        "fields": [
                            "namespace",
                            "limits.cpu-hard",
                            "limits.cpu-used",
                            "cores-usage",
                            "limits.memory-hard",
                            "limits.memory-used",
                            "memory-usage"
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
                "name": f"os-cluster-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                "label": cluster['cluster'],
                "description": f'openshift cluster {cluster["cluster"]}'
            }

            create_type = cmdb_api('POST', 'types/', cmdbToken, data_type_template)

            print(create_type)

            # allTypesPages = getInfoFromAllPage('types', cmdbToken)[0]['pager']['total_pages']
            # newAllTypesPages = list()
            # for page in range(1, allTypesPages + 1):
            #     responsePage = cmdb_api('GET', f'types/?page={page}', cmdbToken)
            #     newAllTypesPages.append(responsePage)

            # newTypeId = None
            # for newTypes in newAllTypesPages:
            #     for newItem in newTypes['results']:
            #         if newItem['name'] == f"os-cluster-{portal_name}--{cluster['cluster'].replace('.', '_')}":
            #             newTypeId = newItem['public_id']

            print(create_type['result_id'], 'new type id')

            # osPortalCategorieId = category_id(f'OS-{portal_name}', f'OS-{portal_name}', 'far fa-folder-open',
            #                                       osPassportsCategorieId['public_id'], all_categories)
            dataCatTemplate: dict = {
                "public_id": osPortalCategorieId['public_id'],
                "name": osPortalCategorieId['name'],
                "label": osPortalCategorieId['label'],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": osPassportsCategorieId['public_id'],
                "types": osPortalCategorieId['types']
            }
            #
            if create_type['result_id'] == None:
                return

            dataCatTemplate['types'].append(create_type['result_id'])

            putTypeInCatigories = cmdb_api('PUT', f"categories/{osPortalCategorieId['public_id']}", cmdbToken,
                                              dataCatTemplate)
            print('putTypeInCatigories', putTypeInCatigories)
            print('dataCatTemplate', dataCatTemplate)

            for namespace in cluster['info']:
                createObject = objects(namespace, cmdbToken, create_type['result_id'], userId, 'NAMESPACE')
                print(createObject)
                time.sleep(0.1)

    # all_objects = getInfoFromAllPage('objects', cmdbToken)
    # from objects import all_objects

    # from pymongo import MongoClient
    # connection_sring = 'mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb'
    # cluster = MongoClient(connection_sring)
    # db = cluster['cmdb']
    # bdObjects = db.get_collection('framework.objects')
    #
    # all_objects = tuple(bdObjects.find({}))
    from vm_passport import get_mongodb_objects
    all_objects = get_mongodb_objects('framework.objects')


    cmdb_projects = getInfoFromAllPage('types', cmdbToken)
    allCmdbClusterTypes = reduce(lambda x, y: x + y,
                                    map(lambda z: tuple(
                                        filter(lambda f: f'os-cluster-{portal_name}--' in f['name'], z['results'])),
                                        cmdb_projects))

    for cmdbCluster in allCmdbClusterTypes:
        for cluster in os_info:
            if cmdbCluster['label'] == cluster['cluster']:
                # print(cmdbCluster['label'], cluster['cluster'])

                # cmdb_namespaces = tuple(filter(lambda f: f['type_id'] == cmdbCluster['public_id'],
                #                                reduce(lambda x, y: x + y, map(lambda z: tuple(
                #                                    map(lambda j: dict(public_id=j.get('public_id'),
                #                                                       type_id=j.get('type_id'),
                #                                                       author_id=j.get('author_id'),
                #                                                       fields=j.get('fields'),
                #                                                       creation_time=j.get('creation_time')),
                #                                        z['results'])), all_objects))))
                cmdbNamespaces = tuple(filter(lambda x: x['type_id'] == cmdbCluster['public_id'], all_objects))
                for osNamespace in cluster['info']:
                    if osNamespace['namespace'] not in map(lambda x: x.get('fields')[0]['value'], cmdbNamespaces):
                        print('NAMESPACE FOR CREATE', osNamespace['namespace'])
                        objects(osNamespace, cmdbToken, cmdbCluster['public_id'], userId, 'NAMESPACE')
                        time.sleep(0.1)

                    for cmdbNs in cmdbNamespaces:
                        nsTemplate = objects(osNamespace, cmdbToken, cmdbCluster['public_id'], userId,
                                              'NAMESPACE', template=True)
                        if cmdbNs['fields'][0]['value'] == osNamespace['namespace'] and cmdbNs['fields'] != \
                                nsTemplate['fields']:
                            # unixTime = lambda x: int(datetime.datetime.timestamp(x) * 1000)
                            # print(unixTime(cmdbNs['creation_time']))

                            updateObjectTemplate: dict = {
                                "type_id": cmdbNs['type_id'],
                                "status": True,
                                "version": "1.0.1",
                                "creation_time": {
                                    # "$date": int(time.mktime(time.strptime(cmdbNs['creation_time'], '%Y-%m-%dT%H:%M:%S.%f')) * 1000)
                                    "$date": int(datetime.datetime.timestamp(cmdbNs['creation_time']) * 1000)
                                },
                                "author_id": cmdbNs['author_id'],
                                "last_edit_time": {
                                    "$date": int(time.time() * 1000)
                                },
                                "editor_id": userId,
                                "active": True,
                                "fields": nsTemplate['fields'],
                                "public_id": cmdbNs['public_id'],
                                "views": 0,
                                "comment": ""
                            }

                            # json_read(updateObjectTemplate)
                            time.sleep(0.1)
                            print(f"UPDATE NAMESPACE in {cmdbNs['type_id']}", osNamespace['namespace'])
                            objects(updateObjectTemplate, cmdbToken, cmdbCluster['public_id'], userId, 'PUT')

                for cmdbNs in cmdbNamespaces:
                    if cmdbNs['fields'][0]['value'] not in map(lambda x: x['namespace'], cluster['info']):
                        print('DELETE NAMESPACE', cmdbNs['fields'][0]['value'])
                        cmdb_api('DELETE', f"object/{cmdbNs['public_id']}", cmdbToken)
                        time.sleep(0.1)
