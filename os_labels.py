#!/usr/bin/python3

import json
import time
import socket
import requests
from functools import reduce
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from env import portal_info
from vm_passport import cmdb_api
# from vm_passport import objects
from vm_passport import categorie_id
from vm_passport import get_cmdb_token
from vm_passport import get_info_from_all_page

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def json_read(json_object: dict):
    print(json.dumps(json_object, indent=4))


# def LabelsOS(portal_name: str, clusters: tuple = (), all_objects: tuple = ()) -> None:
def LabelsOS(portal_name: str, all_objects: tuple) -> None:
    """main func for autocomplete labels in DataGerry"""

    def CreateLabels(labels_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
                     template: bool = False) -> dict:
        if method == 'PUT':
            # return cmdb_api(method, f'object/{labels_info["public_id"]}', cmdb_token, labels_info)
            print(f'object/{labels_info["public_id"]}')

        # print(labels_info)

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

        labelObjectTemplate: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "namespace",
                    "value": getLabel(labels_info, 'namespace')
                },
                {
                    "name": "name",
                    "value": getLabel(labels_info, 'name')
                },
                {
                    "name": "app",
                    "value": getLabel(labels_info, 'app')
                },
                {
                    "name": "SUBSYSTEM",
                    "value": getLabel(labels_info, 'SUBSYSTEM')

                },
                {
                    "name": "deployment",
                    "value": getLabel(labels_info, 'deployment')
                },
                {
                    "name": "deploymentconfig",
                    "value": getLabel(labels_info, 'deploymentconfig')
                },
                {
                    "name": "deployDate",
                    "value": getLabel(labels_info, 'deployDate')
                },
                {
                    "name": "distribVersion",
                    "value": getLabel(labels_info, 'distribVersion')
                },
                {
                    "name": "version",
                    "value": getLabel(labels_info, 'version')
                },
                {
                    "name": "security.istio.io/tlsMode",
                    "value": getLabel(labels_info, 'security.istio.io/tlsMode')
                },
                {
                    "name": "jenkinsDeployUser",
                    "value": getLabel(labels_info, 'jenkinsDeployUser')
                }
            ]
        }
        # json_read(labelObjectTemplate)

        if template:
            return labelObjectTemplate

        return cmdb_api('POST', 'object/', cmdb_token, labelObjectTemplate)
        # json_read(labelObjectTemplate)

        # return labelObjectTemplate
        # print(response.status_code)
        # print(response.json())

    cmdb_token, user_id = get_cmdb_token()
    all_categories = get_info_from_all_page('categories', cmdb_token)

    os_passports_categorie_id = categorie_id('os-app-labels', 'OS App Labels', 'fas fa-tags', cmdb_token,
                                             all_categories)

    os_portal_categorie_id = categorie_id(f'OS-Labels-{portal_name}', f'OS-Labels-{portal_name}', 'fas fa-folder-open',
                                          cmdb_token, all_categories,
                                          os_passports_categorie_id['public_id'])

    def get_os_info() -> dict:
        return json.loads(requests.request("GET", portal_info[portal_name]['metrics']).content)

    cluster_info = get_os_info()
    clusters = map(lambda x: x['metric']['cluster'], cluster_info['data']['result'])

    def getOsLabels(clusters: map) -> list:
        """function of getting pod labels from all clusters"""

        allLabels = list()

        def check_resolves(dnsName: str) -> bool:
            """function for checking resolving dns names"""
            try:
                socket.gethostbyname(dnsName)
                return True
            except socket.error as Error:
                print(dnsName, Error)
                return False

        for cluster_name in set(clusters):
            if check_resolves(f'query-runner.apps.{cluster_name}'):
                get_labels = requests.request("GET", f'https://query-runner.apps.{cluster_name}/pods', verify=False)
                if get_labels.status_code == 200:
                    allLabels.append(dict(cluster=cluster_name, labels=json.loads(get_labels.content)))

        return allLabels

    allLabels = getOsLabels(clusters)


    # print(allLabels)
    # return
    # from allLabels import allLabels

    cmdb_projects = get_info_from_all_page('types', cmdb_token)

    for cluster in allLabels:
        if not any(map(lambda x: any(
                map(lambda y: y['name'] == f"os-labels-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                    x['results'])), cmdb_projects)):  # and cluster['cluster'] == 'ocp.dev.minsport.tech':
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

            all_types_pages = get_info_from_all_page('types', cmdb_token)[0]['pager']['total_pages']

            new_all_types_pages = list()
            for page in range(1, all_types_pages + 1):
                response_page = cmdb_api('GET', f'types/?page={page}', cmdb_token)
                new_all_types_pages.append(response_page)

            new_type_id = None
            for new_types in new_all_types_pages:
                for new_item in new_types['results']:
                    if new_item['name'] == f"os-labels-{portal_name}--{cluster['cluster'].replace('.', '_')}":
                        new_type_id = new_item['public_id']

            print(new_type_id, 'new type id')

            # os_portal_categorie_id = categorie_id(f'OS-Labels-{portal_name}', f'OS-Labels-{portal_name}',
            #                                       'far fa-folder-open',
            #                                       os_passports_categorie_id['public_id'], all_categories)

            # print(os_portal_categorie_id)

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
            #
            if new_type_id == None:
                return

            data_cat_template['types'].append(new_type_id)

            put_type_in_catigories = cmdb_api('PUT', f"categories/{os_portal_categorie_id['public_id']}", cmdb_token,
                                              data_cat_template)

            print('put_type_in_catigories', put_type_in_catigories)
            print('data_cat_template', data_cat_template)
            #############################################################################################################

            # new_type_id = 1062
            for labels in cluster['labels']:
                create_object = CreateLabels(labels, cmdb_token, new_type_id, user_id)
                print(create_object)
                time.sleep(0.1)

    # all_objects = get_info_from_all_page('objects', cmdb_token)

    # from allObjects import allObjects as all_objects

    cmdb_projects = get_info_from_all_page('types', cmdb_token)

    allTypesLabels = reduce(lambda x, y: x + y, map(lambda foo: tuple(
        filter(lambda bar: f'os-labels-{portal_name}--' in bar['name'], foo['results'])), cmdb_projects))

    def formatPodName(podInfo: list) -> list:
        podInfoTmp = podInfo[:]
        podInfoTmp[1]['value'] = podInfo[1]['value'][:-6]
        if podInfo[5]['value']:
            numberValue = 0
            for value in podInfo[1]['value'][::-1]:
                numberValue += 1
                if value == '-':
                    podInfoTmp[1]['value'] = podInfo[1]['value'][:-numberValue]
                    return podInfoTmp
        return podInfoTmp

    for cmdb_cluster in allTypesLabels:
        # if cmdb_cluster['label'] == 'ocp.test.minsport.tech':
        if cmdb_cluster['label'] != 'ocp.business.tech1111111':
            for cluster in allLabels:
                if cmdb_cluster['label'] == cluster['cluster']:
                    cmdb_namespaces = tuple(filter(
                        lambda f: f['type_id'] == cmdb_cluster['public_id'],
                        reduce(lambda x, y: x + y, map(lambda z: tuple(map(lambda j:
                                                                           dict(public_id=j.get('public_id'),
                                                                                type_id=j.get('type_id'),
                                                                                author_id=j.get('author_id'),
                                                                                fields=j.get('fields'),
                                                                                creation_time=j.get('creation_time')),
                                                                           z['results'])), all_objects))))
                    for podInfo in cluster['labels']:
                        # if podInfo['name'] not in map(lambda x: x.get('fields')[1]['value'], cmdb_namespaces):
                        # if podInfo['name'] not in map(lambda x: x.get('fields'), cmdb_namespaces):
                        template = CreateLabels(podInfo, cmdb_token, cmdb_cluster['public_id'], user_id, template=True)
                        # template['fields'][1]['value'] = template['fields'][1]['value'][:-6]
                        # print(template['fields'][1]['value'])
                        # tmpField = formatPodName(template['fields'])
                        # if tmpField not in map(lambda x: formatPodName(x.get('fields')), cmdb_namespaces):
                        if template['fields'] not in map(lambda x: x.get('fields'), cmdb_namespaces):
                            createLabel = CreateLabels(podInfo, cmdb_token, cmdb_cluster['public_id'], user_id)
                            print('Create Label', template['fields'][1]['value'], createLabel)
                            time.sleep(0.1)

                    for cmdbLabel in cmdb_namespaces:
                        if cmdbLabel['fields'][1]['value'] not in map(lambda x: x['name'], cluster['labels']):
                            print('Delete Label', cmdbLabel['fields'][1]['value'])
                            print(cmdb_api('DELETE', f"object/{cmdbLabel['public_id']}", cmdb_token))
                            time.sleep(0.1)

                    # print(tmpField[1]['value'])
                    # print(podInfo['name'])
                    # print('########' * 10)

                    # for i in map(lambda x: x.get('fields'), cmdb_namespaces):
                    #     print(i)

                    # cmdbPodsTmp = tuple(map(lambda x: formatPodName(x.get('fields'))[1]['value'], cmdb_namespaces))
                    # samePods = {i: cmdbPodsTmp.count(i) for i in cmdbPodsTmp}
                    # json_read(samePods)

                    # for podInfo1 in cluster['labels']:
                    #     print(podInfo1['labels']['name'])

                    # print(template['fields'][1]['value'])

                    # print(template['fields'][1]['value'])
                    # print(template['fields'])
                    # print('####' * 10)

                    # tmpCmdbNsFields = list(
                    #     map(lambda x: formatPodName(x), map(lambda x: x.get('fields'), cmdb_namespaces)))

                    # tmpCmdbNsFields = list()
                    # for cmdb_namespace in cmdb_namespaces:
                    #     tmpCmdbNsFields.append(cmdb_namespace['fields'])
                    #
                    # tmpCmdbNsPodNames = list()
                    # for fields in tmpCmdbNsFields:
                    #     tmpCmdbNsPodNames.append(formatPodName(fields))

                    # for name in tmpCmdbNsPodNames:
                    #     print(name[1])

                    # del tmpCmdbNsPodNames
                    # del tmpCmdbNsFields

                    # map(lambda x: formatPodName(x), map(lambda x: print(x.get('fields')), cmdb_namespaces)))

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
                    #     k  = formatPodName(i)
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

                    # if template['fields'] not in list(map(lambda x: formatPodName(x), map(lambda x: x.get('fields'), cmdb_namespaces))):

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

                    # print('CREATE LABEL', podInfo['name'], podInfo['namespace'])
                    # json_read(podInfo)
                    # json_read(template['fields'])

                    # print(podInfo['namespace'])

                    # print(template['fields'][1]['value'])
                    # print(template['fields'])

                    # print(template['fields'][1]['value'][:-6])

                    # print(type(template['fields']))
                    # json_read(list(map(lambda x: x.get('fields'), cmdb_namespaces)))

                    # return
                    # create_namespace = CreateLabels(podInfo, cmdb_token, cmdb_cluster['public_id'], user_id)
                    # print(create_namespace)
                    # return

                    # for cmdb_ns in cmdb_namespaces:
                    #     label_template = \
                    #         CreateLabels(podInfo, cmdb_token, cmdb_cluster['public_id'], user_id, template=True)
                    #
                    #     if cmdb_ns['fields'][0]['value'] == podInfo['namespace'] and cmdb_ns['fields'] != \
                    #             label_template['fields']:
                    # print(label_template)
                    # print(f"UPDATE NAMESPACE in {cmdb_ns['type_id']}", podInfo['namespace'])
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


if __name__ == '__main__':
    LabelsOS('PD15')
