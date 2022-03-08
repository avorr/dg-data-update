#!/usr/bin/python3

import json
import time
import socket
import requests
from functools import reduce
from pymongo import MongoClient
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from env import portal_info
from vm_passport import cmdb_api
# from vm_passport import objects
from vm_passport import category_id
from vm_passport import get_dg_token
from vm_passport import get_all_jsons
from vm_passport import get_mongodb_objects

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def json_read(json_object: dict):
    print(json.dumps(json_object, indent=4))


# def LabelsOS(portal_name: str, clusters: tuple = (), all_objects: tuple = ()) -> None:
def LabelsOS(portal_name: str, all_objects: tuple = ()) -> None:
    """main func for autocomplete labels in DataGerry"""

    def CreateLabels(labels_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
                     template: bool = False) -> dict:

        if method == 'PUT':
            # return cmdb_api(method, f'object/{labels_info["public_id"]}', cmdb_token, labels_info)
            print(f'object/{labels_info["public_id"]}')

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

        # namespace
        # name
        # app
        # SUBSYSTEM
        # deployment
        # deploymentconfig
        # deployDate
        # distribVersion
        # version
        # security.istio.io/tlsMode
        # jenkinsDeployUser

        label_object_template: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "namespace",
                    "value": get_label(labels_info, 'namespace')
                },
                {
                    "name": "name",
                    "value": get_label(labels_info, 'name')
                },
                {
                    "name": "app",
                    "value": get_label(labels_info, 'app')
                },
                {
                    "name": "SUBSYSTEM",
                    "value": get_label(labels_info, 'SUBSYSTEM')

                },
                {
                    "name": "deployment",
                    "value": get_label(labels_info, 'deployment')
                },
                {
                    "name": "deploymentconfig",
                    "value": get_label(labels_info, 'deploymentconfig')
                },
                {
                    "name": "deployDate",
                    "value": get_label(labels_info, 'deployDate')
                },
                {
                    "name": "distribVersion",
                    "value": get_label(labels_info, 'distribVersion')
                },
                {
                    "name": "version",
                    "value": get_label(labels_info, 'version')
                },
                {
                    "name": "security.istio.io/tlsMode",
                    "value": get_label(labels_info, 'security.istio.io/tlsMode')
                },
                {
                    "name": "jenkinsDeployUser",
                    "value": get_label(labels_info, 'jenkinsDeployUser')
                }
            ]
        }

        if template:
            return label_object_template

        return cmdb_api('POST', 'object/', cmdb_token, label_object_template)

        # print(response.status_code)
        # print(response.json())

    cmdb_token, user_id = get_dg_token()

    from vm_passport import get_mongodb_objects
    all_categories = get_mongodb_objects('framework.categories')

    os_passports_category_id: dict = \
        category_id('os-app-labels', 'OS App Labels', 'fas fa-tags', cmdb_token, all_categories)

    os_portal_category_id: dict = \
        category_id(f'OS-Labels-{portal_name}', f'OS-Labels-{portal_name}', 'fas fa-folder-open', cmdb_token,
                    all_categories, os_passports_category_id['public_id'])

    def get_os_info() -> dict:
        return json.loads(requests.request("GET", portal_info[portal_name]['metrics']).content)

    cluster_info = get_os_info()
    clusters = map(lambda x: x['metric']['cluster'], cluster_info['data']['result'])

    def get_ose_labels(clusters: map) -> list:
        """
        function for getting pod labels from all clusters
        :param clusters:
        :return: list
        """

        all_labels = list()

        def check_resolves(dns_name: str) -> bool:
            """
            function for checking resolving dns names
            :param dns_name:
            :return: bool
            """
            try:
                socket.gethostbyname(dns_name)
                return True
            except socket.error as Error:
                print(dns_name, Error)
                return False

        for cluster_name in set(clusters):
            if check_resolves('query-runner.apps.%s' % cluster_name):
                get_labels = requests.request("GET", f'https://query-runner.apps.{cluster_name}/pods', verify=False)
                if get_labels.status_code == 200:
                    all_labels.append(dict(cluster=cluster_name, labels=json.loads(get_labels.content)))

        return all_labels

    all_labels: list = get_ose_labels(clusters)

    # print(all_labels)
    # return
    # from all_labels import all_labels
    # cmdb_projects = get_all_jsons('types', cmdb_token)

    cmdb_projects: tuple = get_mongodb_objects("framework.types")

    for cluster in all_labels:
        # if not any(map(lambda x: any(map(lambda y: y['name'] == f"os-labels-{portal_name}--{cluster['cluster'].replace('.', '_')}", x['results'])), cmdb_projects)):
        if not any(map(lambda y: y['name'] == f"os-labels-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                       cmdb_projects)):
            # and cluster['cluster'] == 'ocp.dev.minsport.tech':

            ##############################################################################################################

            data_type_template: dict = {
                "fields": [
                    {
                        "type": "text",
                        "name": "namespace",
                        "label": "namespace"
                    },
                    {
                        "type": "text",
                        "name": "name",
                        "label": "name"
                    },
                    {
                        "type": "text",
                        "name": "app",
                        "label": "app"
                    },
                    {
                        "type": "text",
                        "name": "SUBSYSTEM",
                        "label": "SUBSYSTEM"
                    },
                    {
                        "type": "text",
                        "name": "deployment",
                        "label": "deployment"
                    },
                    {
                        "type": "text",
                        "name": "deploymentconfig",
                        "label": "deploymentconfig"
                    },
                    {
                        "type": "text",
                        "name": "deployDate",
                        "label": "deployDate"
                    },
                    {
                        "type": "text",
                        "name": "distribVersion",
                        "label": "distribVersion"
                    },
                    {
                        "type": "text",
                        "name": "version",
                        "label": "version"
                    },
                    {
                        "type": "text",
                        "name": "security.istio.io/tlsMode",
                        "label": "security.istio.io/tlsMode"
                    },
                    {
                        "type": "text",
                        "name": "jenkinsDeployUser",
                        "label": "jenkinsDeployUser"
                    }
                ],
                "active": True,
                "version": "1.0.0",
                "author_id": user_id,
                "render_meta": {
                    "icon": "fas fa-dharmachakra",
                    "sections": [
                        {
                            "fields": [
                                "namespace",
                                "name",
                                "app",
                                "SUBSYSTEM",
                                "deployment",
                                "deploymentconfig",
                                "deployDate",
                                "distribVersion",
                                "version",
                                "security.istio.io/tlsMode",
                                "jenkinsDeployUser"
                            ],
                            "type": "section",
                            "name": f"os-labels-{portal_name}--{cluster['cluster']}",
                            "label": cluster['cluster']
                        }
                    ],
                    "externals": [],
                    "summary": {
                        "fields": [
                            "namespace",
                            "name",
                            "app",
                            "SUBSYSTEM",
                            "deployment",
                            "deploymentconfig",
                            "deployDate",
                            "distribVersion",
                            "version",
                            "security.istio.io/tlsMode",
                            "jenkinsDeployUser"
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
                "name": f"os-labels-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                "label": cluster['cluster'],
                "description": f'openshift labels {cluster["cluster"]}'
            }

            create_type = cmdb_api('POST', 'types/', cmdb_token, data_type_template)

            print(create_type)

            print(create_type['result_id'], 'new type id')

            data_cat_template: dict = {
                "public_id": os_portal_category_id['public_id'],
                "name": os_portal_category_id['name'],
                "label": os_portal_category_id['label'],
                "meta": {
                    "icon": "fas fa-folder-open",
                    "order": None
                },
                "parent": os_passports_category_id['public_id'],
                "types": os_portal_category_id['types']
            }
            #
            if not create_type['result_id']:
                return

            data_cat_template['types'].append(create_type['result_id'])

            put_type_in_category = cmdb_api('PUT', f"categories/{os_portal_category_id['public_id']}", cmdb_token,
                                              data_cat_template)

            print('PUT TYPE IN CATEGORY', put_type_in_category)
            print('DATA CATEGORY TEMPLATE', data_cat_template)
            #############################################################################################################

            # create_type['result_id'] = 1062
            for labels in cluster['labels']:
                create_object = CreateLabels(labels, cmdb_token, create_type['result_id'], user_id)
                print('CREATE OBJECT', create_object)
                time.sleep(0.1)

    # all_objects = None
    # all_objects = get_all_jsons('objects', cmdb_token)

    # connection_sring = 'mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb'
    # cluster = MongoClient(connection_sring)
    # db = cluster['cmdb']
    # bdObjects = db.get_collection('framework.objects')
    # all_objects = tuple(bdObjects.find({}))

    # from allObjects import allObjects as all_objects
    # from vm_passport import get_mongodb_objects

    all_objects = get_mongodb_objects('framework.objects')

    # cmdb_projects = get_all_jsons('types', cmdb_token)
    # cmdb_projects: tuple = get_mongodb_objects("framework.types")

    # all_types_labels = reduce(lambda x, y: x + y, map(lambda foo: tuple(filter(lambda bar: f'os-labels-{portal_name}--' in bar['name'], foo['results'])), cmdb_projects))
    all_types_labels = tuple(filter(lambda x: f'os-labels-{portal_name}--' in x['name'], cmdb_projects))

    def format_pod_name(pod_info: list) -> list:
        pod_info_tmp = pod_info[:]
        pod_info_tmp[1]['value'] = pod_info[1]['value'][:-6]
        if pod_info[5]['value']:
            number_value = 0
            for value in pod_info[1]['value'][::-1]:
                number_value += 1
                if value == '-':
                    pod_info_tmp[1]['value'] = pod_info[1]['value'][:-number_value]
                    return pod_info_tmp
        return pod_info_tmp

    for cmdb_cluster in all_types_labels:
        for cluster in all_labels:
            if cmdb_cluster['label'] == cluster['cluster']:

                # cmdb_namespaces = tuple(filter(
                #     lambda f: f['type_id'] == cmdb_cluster['public_id'],
                #     reduce(lambda x, y: x + y, map(lambda z: tuple(map(lambda j:
                #                                                        dict(public_id=j.get('public_id'),
                #                                                             type_id=j.get('type_id'),
                #                                                             author_id=j.get('author_id'),
                #                                                             fields=j.get('fields'),
                #                                                             creation_time=j.get('creation_time')),
                #                                                        z['results'])), all_objects))))

                cmdb_namespaces = tuple(filter(lambda x: x['type_id'] == cmdb_cluster['public_id'], all_objects))

                for pod_info in cluster['labels']:
                    # if pod_info['name'] not in map(lambda x: x.get('fields')[1]['value'], cmdb_namespaces):
                    # if pod_info['name'] not in map(lambda x: x.get('fields'), cmdb_namespaces):
                    template = CreateLabels(pod_info, cmdb_token, cmdb_cluster['public_id'], user_id, template=True)
                    # template['fields'][1]['value'] = template['fields'][1]['value'][:-6]
                    # print(template['fields'][1]['value'])
                    # tmpField = format_pod_name(template['fields'])
                    # if tmpField not in map(lambda x: format_pod_name(x.get('fields')), cmdb_namespaces):
                    if template['fields'] not in map(lambda x: x.get('fields'), cmdb_namespaces):
                        createLabel = CreateLabels(pod_info, cmdb_token, cmdb_cluster['public_id'], user_id)
                        print('CREATE LABEL <--->', template['fields'][1]['value'], createLabel)
                        time.sleep(0.1)

                for cmdb_label in cmdb_namespaces:
                    if cmdb_label['fields'][1]['value'] not in map(lambda x: x['name'], cluster['labels']):
                        print('DELETE LABEL <--->', cmdb_label['fields'][1]['value'])
                        cmdb_api('DELETE', f"object/{cmdb_label['public_id']}", cmdb_token)
                        time.sleep(0.1)

                # print(tmpField[1]['value'])
                # print(pod_info['name'])
                # print('########' * 10)

                # for i in map(lambda x: x.get('fields'), cmdb_namespaces):
                #     print(i)

                # cmdbPodsTmp = tuple(map(lambda x: format_pod_name(x.get('fields'))[1]['value'], cmdb_namespaces))
                # samePods = {i: cmdbPodsTmp.count(i) for i in cmdbPodsTmp}
                # json_read(samePods)

                # for pod_info1 in cluster['labels']:
                #     print(pod_info1['labels']['name'])

                # print(template['fields'][1]['value'])

                # print(template['fields'][1]['value'])
                # print(template['fields'])
                # print('####' * 10)

                # tmpCmdbNsFields = list(
                #     map(lambda x: format_pod_name(x), map(lambda x: x.get('fields'), cmdb_namespaces)))

                # tmpCmdbNsFields = list()
                # for cmdb_namespace in cmdb_namespaces:
                #     tmpCmdbNsFields.append(cmdb_namespace['fields'])
                #
                # tmpCmdbNsPodNames = list()
                # for fields in tmpCmdbNsFields:
                #     tmpCmdbNsPodNames.append(format_pod_name(fields))

                # for name in tmpCmdbNsPodNames:
                #     print(name[1])

                # del tmpCmdbNsPodNames
                # del tmpCmdbNsFields

                # map(lambda x: format_pod_name(x), map(lambda x: print(x.get('fields')), cmdb_namespaces)))

                # print(tmpCmdbNsFields)

                # for i in tmpCmdbNsFields:
                #     print(i[1])

                # for i in map(lambda x: x[1]['value'], tmpCmdbNsFields):
                #     print(i)
                # pass

                # print(list(map(lambda x: x[1]['value'], tmpCmdbNsFields)))

                # if f"{template['fields'][1]['value']}" not in map(lambda x: x[1]['value'], tmpCmdbNsFields):
                # print(True)
                # pass
                # else:
                # print(False)
                # pass
                #
                # print(template['fields'][1]['value'])
                #
                # return

                # for i in map(lambda x: x.get('fields'), cmdb_namespaces):
                #     k  = format_pod_name(i)
                #     print(k)

                # print(list(map(lambda x: x[1].get('value'), tmpCmdbNsFields)))
                # return
                # for s in map(lambda x: x[1].get('value'), tmpCmdbNsFields):
                #     print(s)
                # print(list(map(lambda x: x[1].get('value'), tmpCmdbNsFields)))
                # tmpPodName = list(map(lambda x: x[1].get('value'), tmpCmdbNsFields))
                # print(tmpPodName)
                # return
                # print(list(tmpCmdbNsFields))

                # if template['fields'] not in list(map(lambda x: format_pod_name(x), map(lambda x: x.get('fields'), cmdb_namespaces))):

                # print(template['fields'][1]['value'])

                # for i in list(map(lambda x: x[1].get('value'), tmpCmdbNsFields)):
                #     print(i)
                # print(template['fields'][1]['value'])

                # foo = list(map(lambda x: x[1].get('value'), tmpCmdbNsFields))
                # print(foo)

                # if f"{template['fields'][1]['value']}" not in map(lambda x: x[1]['value'], tmpCmdbNsFields):
                #     q += 1
                # print(template['fields'][1]['value'])

                # print(q)

                # return

                # print(i)

                # print(template['fields'])
                # print(template['fields'])

                # print('CREATE LABEL', pod_info['name'], pod_info['namespace'])
                # json_read(pod_info)
                # json_read(template['fields'])

                # print(pod_info['namespace'])

                # print(template['fields'][1]['value'])
                # print(template['fields'])

                # print(template['fields'][1]['value'][:-6])

                # print(type(template['fields']))
                # json_read(list(map(lambda x: x.get('fields'), cmdb_namespaces)))

                # return
                # create_namespace = CreateLabels(pod_info, cmdb_token, cmdb_cluster['public_id'], user_id)
                # print(create_namespace)
                # return

                # for cmdb_ns in cmdb_namespaces:
                #     label_template = \
                #         CreateLabels(pod_info, cmdb_token, cmdb_cluster['public_id'], user_id, template=True)
                #
                #     if cmdb_ns['fields'][0]['value'] == pod_info['namespace'] and cmdb_ns['fields'] != \
                #             label_template['fields']:
                # print(label_template)
                # print(f"UPDATE NAMESPACE in {cmdb_ns['type_id']}", pod_info['namespace'])
                #
                # unixTime = lambda x: int(
                #     time.mktime(time.strptime(x, '%Y-%m-%dT%H:%M:%S.%f')) * 1000) if '.' in x \
                #     else int(time.mktime(time.strptime(x, '%Y-%m-%dT%H:%M:%S')) * 1000)
                #
                # updateObjectTmp: dict = {
                #     "type_id": cmdb_ns['type_id'],
                #     "status": True,
                #     "version": "1.0.1",
                #     "creation_time": {
                # "$date": int(time.mktime(time.strptime(cmdb_ns['creation_time'], '%Y-%m-%dT%H:%M:%S.%f')) * 1000)
                # "$date": unixTime(cmdb_ns['creation_time'])
                # },
                # "author_id": cmdb_ns['author_id'],
                # "last_edit_time": {
                #     "$date": int(time.time() * 1000)
                # },
                # "editor_id": user_id,
                # "active": True,
                # "fields": label_template['fields'],
                # "public_id": cmdb_ns['public_id'],
                # "views": 0,
                # "comment": ""
                # }
                # print(i)
                # print(updateObjectTmp)
                # print(CreateLabels(updateObjectTmp, cmdb_token, cmdb_cluster['public_id'], user_id, 'PUT'))

                # for cmdb_ns in cmdb_namespaces:
                #     if cmdb_ns['fields'][0]['value'] not in map(lambda x: x['namespace'], cluster['info']):
                #         print('OBJECT for Delete', cmdb_ns['fields'][0]['value'])
                #         print(cmdb_api('DELETE', f"object/{cmdb_ns['public_id']}", cmdb_token))
