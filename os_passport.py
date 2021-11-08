#!/usr/bin/python3

import json
import time
import requests
from functools import reduce
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from env import portal_info
from vm_passport import cmdb_api
from vm_passport import objects
from vm_passport import categorie_id
from vm_passport import get_cmdb_token
from vm_passport import get_info_from_all_page

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def json_read(json_object: dict):
    print(json.dumps(json_object, indent=4))


def PassportsOS(portal_name: str):
    cmdb_token, user_id = get_cmdb_token()
    all_categories = get_info_from_all_page('categories', cmdb_token)

    os_passports_categorie_id = categorie_id('passports-os', 'Passports OpenShift', 'fab fa-redhat', cmdb_token, all_categories)
    os_portal_categorie_id = categorie_id(f'OS-{portal_name}', f'OS-{portal_name}', 'far fa-folder-open', cmdb_token, all_categories,
                                          os_passports_categorie_id['public_id'])

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
                if item['cluster'] == metric['metric']['cluster'] and info['namespace'] == metric['metric'][
                    'namespace']:
                    info['info'].append((metric['metric']['resource'], metric['metric']['type'], metric['value']))


    cmdb_projects = get_info_from_all_page('types', cmdb_token)

    for cluster in os_info:

        if not any(map(lambda x: any(
                map(lambda y: y['name'] == f"os-cluster--{cluster['cluster'].replace('.', '_')}", x['results'])),
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
                            "name": f"os-cluster--{cluster['cluster']}",
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
                "name": f"os-cluster--{cluster['cluster'].replace('.', '_')}",
                "label": cluster['cluster'],
                "description": f'openshift cluster {cluster["cluster"]}'
            }

            create_type = cmdb_api('POST', 'types/', cmdb_token, data_type_template)
            print(create_type)
            all_types_pages = get_info_from_all_page('types')[0]['pager']['total_pages']
            new_all_types_pages = list()
            for page in range(1, all_types_pages + 1):
                response_page = cmdb_api('GET', f'types/?page={page}', cmdb_token)
                new_all_types_pages.append(response_page)

            new_type_id = None
            for new_types in new_all_types_pages:
                for new_item in new_types['results']:
                    if new_item['name'] == f"os-cluster--{cluster['cluster'].replace('.', '_')}":
                        new_type_id = new_item['public_id']

            print(new_type_id, 'new type id')

            os_portal_categorie_id = categorie_id(f'OS-{portal_name}', f'OS-{portal_name}', 'far fa-folder-open',
                                                  os_passports_categorie_id['public_id'])
            data_cat_template: dict = {
                "public_id": os_portal_categorie_id['public_id'],
                "name": os_portal_categorie_id['name'],
                "label": os_portal_categorie_id['label'],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": os_passports_categorie_id['public_id'],
                "types": os_portal_categorie_id['types']
            }

            if new_type_id == None:
                return

            data_cat_template['types'].append(new_type_id)

            put_type_in_catigories = cmdb_api('PUT', f"categories/{os_portal_categorie_id['public_id']}", cmdb_token,
                                              data_cat_template)
            print(put_type_in_catigories)
            print('data_cat_template', data_cat_template)

            for namespace in cluster['info']:
                create_object = objects(namespace, cmdb_token, new_type_id, user_id, 'NAMESPACE')
                print(create_object)
                time.sleep(0.5)


    all_objects = get_info_from_all_page('objects', cmdb_token)

    cmdb_projects = get_info_from_all_page('types', cmdb_token)
    all_cmdb_cluster_types = reduce(lambda x, y: x + y,
                                    map(lambda x_inner: tuple(
                                        filter(lambda y_inner: 'os-cluster--' in y_inner['name'], x_inner['results'])),
                                        cmdb_projects))


    for cmdb_cluster in all_cmdb_cluster_types:
        for cluster in os_info:
            if cmdb_cluster['label'] == cluster['cluster']:

                cmdb_namespaces = tuple(filter(lambda f: f['type_id'] == cmdb_cluster['public_id'],
                                               reduce(lambda x, y: x + y, map(lambda z: tuple(
                                                   map(lambda j: dict(public_id=j.get('public_id'),
                                                                      type_id=j.get('type_id'),
                                                                      author_id=j.get('author_id'),
                                                                      fields=j.get('fields'),
                                                                      creation_time=j.get('creation_time')),
                                                       z['results'])), all_objects))))


                for os_namespace in cluster['info']:
                    if os_namespace['namespace'] not in map(lambda x: x.get('fields')[0]['value'], cmdb_namespaces):
                        print('NAMESPACE FOR CREATE', os_namespace['namespace'])
                        create_namespace = objects(os_namespace, cmdb_token, cmdb_cluster['public_id'], user_id, 'NAMESPACE')
                        print(create_namespace)

                    for cmdb_ns in cmdb_namespaces:
                        ns_template = objects(os_namespace, cmdb_token, cmdb_cluster['public_id'], user_id,
                                              'NAMESPACE', template=True)
                        if cmdb_ns['fields'][0]['value'] == os_namespace['namespace'] and cmdb_ns['fields'] != \
                                ns_template['fields']:
                            print(f"UPDATE NAMESPACE {cmdb_ns['type_id']}", os_namespace['namespace'])

                            update_object_template: dict = {
                                "type_id": cmdb_ns['type_id'],
                                "status": True,
                                "version": "1.0.1",
                                "creation_time": {
                                    "$date": int(time.mktime(
                                        time.strptime(cmdb_ns['creation_time'], '%Y-%m-%dT%H:%M:%S.%f')) * 1000)
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

                            print(objects(update_object_template, cmdb_token, cmdb_cluster['public_id'], user_id, 'PUT'))

                for cmdb_ns in cmdb_namespaces:
                    if cmdb_ns['fields'][0]['value'] not in map(lambda x: x['namespace'], cluster['info']):
                        print('OBJECT for Delete', cmdb_ns['fields'][0]['value'])
                        print(cmdb_api('DELETE', f"object/{cmdb_ns['public_id']}", cmdb_token))