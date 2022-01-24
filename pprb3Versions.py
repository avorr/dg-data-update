#!/usr/bin/python3

import json
import time
import socket
import requests
from functools import reduce
# from pymongo import MongoClient
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

    # cmdbToken, userId = get_cmdbToken()
    cmdbToken = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOnsiZXNzZW50aWFsIjp0cnVlLCJ2YWx1ZSI6IkRBVEFHRVJSWSJ9LCJpYXQiOjE2NDI5NzE4MDQsImV4cCI6MTY0MzA1NTgwNCwiREFUQUdFUlJZIjp7ImVzc2VudGlhbCI6dHJ1ZSwidmFsdWUiOnsidXNlciI6eyJwdWJsaWNfaWQiOjEwfX19fQ.AxayswC7Je7Dx-ZMr5NCsGWPlOiSp1qcmlQ9MJYKn_CtCvHcRbb1TNb8_2-lBJT_Kbf_t-Ud2jcb1RN6xMioNXUUpNIj1Lu1U5VRAVRE3_aKzBrNy85t0nYUcTB4aIA8whtHPvU1rWtI4XgDM36ry_XB407mG5_3Y70b9yqKKz_NXUhcDiGp1zbgoDfiYlx12672OcVUcrxzRU6jOrKlzddT3YQkn7fU0N6JPhjIukAAcPgY6cs4pQ5A2Jo6WQj5lFsW7wnn4nD8sOJ4-0OPllOoNAdw9wckm035cmIIpdGnrKWgXS7lXYRGaw1mfXBXCJKbqABfyGcVc5qgSdmOew'
    userId = 10
    all_categories = get_info_from_all_page('categories', cmdbToken)

    os_passports_categorie_id = categorie_id('pprb3-app-versions', 'Pprb3 App Versions', 'fas fa-server', cmdbToken,
                                             all_categories)

    os_portal_categorie_id = \
        categorie_id(f'Pprb3-Versions-{portal_name}', f'Pprb3-Versions-{portal_name}', 'far fa-folder-open',
                     cmdbToken, all_categories,
                     os_passports_categorie_id['public_id'])


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

    cmdb_projects = get_info_from_all_page('types', cmdbToken)
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
            all_types_pages = get_info_from_all_page('types', cmdbToken)[0]['pager']['total_pages']

            new_all_types_pages = list()
            for page in range(1, all_types_pages + 1):
                response_page = cmdb_api('GET', f'types/?page={page}', cmdbToken)
                new_all_types_pages.append(response_page)

            newTypeId = None
            for new_types in new_all_types_pages:
                for new_item in new_types['results']:
                    if new_item['name'] == f"pprb3-versions-{portal_name}--{stand['project_id']}":
                        newTypeId = new_item['public_id']
            print(newTypeId, 'new type id')

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

            if newTypeId == None:
                return
            data_cat_template['types'].append(newTypeId)
            put_type_in_catigories = cmdb_api('PUT', f"categories/{os_portal_categorie_id['public_id']}", cmdbToken,
                                              data_cat_template)

            print('PUT TYPE IN CATIGORIES', put_type_in_catigories)
            print('DATA CATATEGORIE TEMPLATE', data_cat_template)

            # return
            # newTypeId = 120
            for version in stand['modules_version']:
                # print(version)
                create_object = CreateObject(version, cmdbToken, newTypeId, userId)
                print('CREATE OBJECT', create_object)
                time.sleep(0.1)
                # return
    return

    # all_objects = None
    # all_objects = get_info_from_all_page('objects', cmdbToken)

    # connection_sring = 'mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb'
    # cluster = MongoClient(connection_sring)
    # db = cluster['cmdb']
    # bdObjects = db.get_collection('framework.objects')
    # all_objects = tuple(bdObjects.find({}))

    # from allObjects import allObjects as all_objects
    from allObjects import all_objects

    cmdb_projects = get_info_from_all_page('types', cmdbToken)

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
        # if cmdb_cluster['label'] != 'ocp.business.tech1111111':
        for cluster in allLabels:
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

                for podInfo in cluster['labels']:
                    # if podInfo['name'] not in map(lambda x: x.get('fields')[1]['value'], cmdb_namespaces):
                    # if podInfo['name'] not in map(lambda x: x.get('fields'), cmdb_namespaces):
                    template = CreateObject(podInfo, cmdbToken, cmdb_cluster['public_id'], userId, template=True)
                    # template['fields'][1]['value'] = template['fields'][1]['value'][:-6]
                    # print(template['fields'][1]['value'])
                    # tmpField = formatPodName(template['fields'])
                    # if tmpField not in map(lambda x: formatPodName(x.get('fields')), cmdb_namespaces):
                    if template['fields'] not in map(lambda x: x.get('fields'), cmdb_namespaces):
                        createLabel = CreateObject(podInfo, cmdbToken, cmdb_cluster['public_id'], userId)
                        print('CREATE LABEL <--->', template['fields'][1]['value'], createLabel)
                        time.sleep(0.1)

                for cmdbLabel in cmdb_namespaces:
                    if cmdbLabel['fields'][1]['value'] not in map(lambda x: x['name'], cluster['labels']):
                        print('DELETE LABEL <--->', cmdbLabel['fields'][1]['value'])
                        cmdb_api('DELETE', f"object/{cmdbLabel['public_id']}", cmdbToken)
                        time.sleep(0.1)


if __name__ == '__main__':
    pprb3Versions(next(iter(portal_info)))
