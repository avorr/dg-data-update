#!/usr/bin/python3

import json
import time
import requests
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from env import portal_info
from vm_passport import cmdb_api
from vm_passport import objects
from vm_passport import category_id
from vm_passport import get_dg_token

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def PassportsOS(portal_name: str, all_objects: tuple) -> None:
    cmdb_token, user_id = get_dg_token()

    from vm_passport import get_mongodb_objects
    all_categories = get_mongodb_objects('framework.categories')

    os_passports_category_id: dict = \
        category_id('passports-os', 'Passports OpenShift', 'fab fa-redhat', cmdb_token, all_categories)
    os_portal_category_id: dict = \
        category_id(f'OS-{portal_name}', f'OS-{portal_name}', 'far fa-folder-open', cmdb_token, all_categories,
                    os_passports_category_id['public_id'])

    def get_os_info() -> dict:
        print(portal_info[portal_name]['metrics'])
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
            info['info'][i] = dict(namespace=namespace, info=list())

    for item in os_info:
        for info in item['info']:
            for metric in cluster_info['data']['result']:
                if item['cluster'] == metric['metric']['cluster'] and \
                        info['namespace'] == metric['metric']['namespace']:
                    info['info'].append((metric['metric']['resource'], metric['metric']['type'], metric['value']))

    cmdb_projects: tuple = get_mongodb_objects('framework.types')

    for cluster in os_info:
        if not any(map(lambda y: y['name'] == f"os-cluster-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                       cmdb_projects)):

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
                "author_id": user_id,
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
                    "externals": [
                        {
                            "name": "cluster link",
                            "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects" %
                                    cluster['cluster'],
                            "label": "Cluster link",
                            "icon": "fas fa-external-link-alt",
                            "fields": []
                        },
                        {
                            "name": "namespace link",
                            "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects/{}" %
                                    cluster['cluster'],
                            "label": "Namespace link",
                            "icon": "fas fa-external-link-alt",
                            "fields": ["namespace"]
                        }
                    ],
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

            create_type = cmdb_api('POST', 'types/', cmdb_token, data_type_template)

            print(create_type['result_id'], 'new type id')

            data_category_template: dict = {
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

            data_category_template['types'].append(create_type['result_id'])

            put_type_in_category = cmdb_api('PUT', f"categories/{os_portal_category_id['public_id']}", cmdb_token,
                                            data_category_template)
            print('put_type_in_category', put_type_in_category)
            print('data_category_template', data_category_template)

            for namespace in cluster['info']:
                create_object = objects(namespace, cmdb_token, create_type['result_id'], user_id, 'NAMESPACE')
                print(create_object)
                time.sleep(0.1)

    all_objects: tuple = get_mongodb_objects('framework.objects')

    all_cmdb_cluster_types = tuple(filter(lambda f: f'os-cluster-{portal_name}--' in f['name'], cmdb_projects))

    for cmdb_cluster in all_cmdb_cluster_types:
        for cluster in os_info:
            if cmdb_cluster['label'] == cluster['cluster']:
                cmdb_namespaces = tuple(filter(lambda x: x['type_id'] == cmdb_cluster['public_id'], all_objects))
                for os_namespace in cluster['info']:
                    if os_namespace['namespace'] not in map(lambda x: x.get('fields')[0]['value'], cmdb_namespaces):
                        print('NAMESPACE FOR CREATE', os_namespace['namespace'])
                        objects(os_namespace, cmdb_token, cmdb_cluster['public_id'], user_id, 'NAMESPACE')
                        time.sleep(0.1)

                    for cmdb_ns in cmdb_namespaces:
                        ns_template = objects(os_namespace, cmdb_token, cmdb_cluster['public_id'], user_id,
                                              'NAMESPACE', template=True)
                        if cmdb_ns['fields'][0]['value'] == os_namespace['namespace'] and cmdb_ns['fields'] != \
                                ns_template['fields']:
                            update_object_template: dict = {
                                "type_id": cmdb_ns['type_id'],
                                "status": cmdb_ns["version"],
                                "version": cmdb_ns["version"],
                                "creation_time": {
                                    "$date": int(datetime.datetime.timestamp(cmdb_ns['creation_time']) * 1000)
                                },
                                "author_id": cmdb_ns['author_id'],
                                "last_edit_time": {
                                    "$date": int(time.time() * 1000)
                                },
                                "editor_id": user_id,
                                "active": cmdb_ns["active"],
                                "fields": ns_template['fields'],
                                "public_id": cmdb_ns['public_id'],
                                "views": cmdb_ns["views"],
                                "comment": ""
                            }

                            time.sleep(0.1)
                            print(f"UPDATE NAMESPACE in {cmdb_ns['type_id']}", os_namespace['namespace'])
                            objects(update_object_template, cmdb_token, cmdb_cluster['public_id'], user_id, 'PUT')

                for cmdb_ns in cmdb_namespaces:
                    if cmdb_ns['fields'][0]['value'] not in map(lambda x: x['namespace'], cluster['info']):
                        print('DELETE NAMESPACE', cmdb_ns['fields'][0]['value'])
                        cmdb_api('DELETE', f"object/{cmdb_ns['public_id']}", cmdb_token)
                        time.sleep(0.1)
