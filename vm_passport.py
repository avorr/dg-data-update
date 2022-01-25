#!/usr/bin/python3

import time
import json
import hashlib
import datetime
import requests
from functools import reduce
# from pymongo import MongoClient
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from env import portal_info


def json_read(json_object: dict):
    print(json.dumps(json_object, indent=4))


def cmdbApi(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
    cmdb_api_url: str = "https://cmdb.common.gos-tech.xyz/rest/"
    headers_cmdb_api: dict = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                       data=json.dumps(payload)).content)


def objects(vmInfo: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
            template: bool = False, tags: list = []) -> dict:
    if method == 'PUT':
        return cmdbApi(method, f'object/{vmInfo["public_id"]}', cmdb_token, vmInfo)

    elif method == 'POST_NEW_VM':

        vmObjectTemplate: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": vmInfo
        }

        return cmdbApi('POST', 'object/', cmdb_token, vmObjectTemplate)

    elif method == 'NAMESPACE':
        def convert_to_gb(bytes):
            foo = float(bytes)
            for i in range(3):
                foo = foo / 1024
            return foo

        def get_metric(ns_info: list, looking_metric: str, type_metric: str) -> str:
            for metric in ns_info:
                if metric[0] == looking_metric and metric[1] == type_metric:
                    return metric[2][1]

        # metric = lambda x, y: filter(lambda foo: foo[2][1] if foo[0] == x and foo[1] == y else None, vmInfo['info'])

        get_usage = lambda x, y: "%.2f" % ((float(x) / float(y)) * 100) if float(y) != 0.0 else str(float(y))

        fract = lambda x: str(int(x)) if x - int(x) == 0 else "%.2f" % x

        namespaceObjectTemplate: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "namespace",
                    "value": vmInfo['namespace']
                },
                {
                    "name": "limits.cpu-hard",
                    "value": get_metric(vmInfo['info'], 'limits.cpu', 'hard')
                },
                {
                    "name": "limits.cpu-used",
                    "value": get_metric(vmInfo['info'], 'limits.cpu', 'used')
                },
                {
                    "name": "cores-usage",
                    # "value": "%.2f" % ((float(get_metric(vmInfo['info'], 'limits.cpu', 'used')) / float(get_metric(vmInfo['info'], 'limits.cpu', 'hard'))) * 100)
                    "value": get_usage(get_metric(vmInfo['info'], 'limits.cpu', 'used'),
                                       get_metric(vmInfo['info'], 'limits.cpu', 'hard'))
                },
                {
                    "name": "limits.memory-hard",
                    "value": fract(convert_to_gb(get_metric(vmInfo['info'], 'limits.memory', 'hard')))
                },
                {
                    "name": "limits.memory-used",
                    "value": fract(convert_to_gb(get_metric(vmInfo['info'], 'limits.memory', 'used')))
                },
                {
                    "name": "memory-usage",
                    # "value": "%.2f" % ((float(get_metric(vmInfo['info'], 'limits.memory', 'used')) / float(get_metric(vmInfo['info'], 'limits.memory', 'hard'))) * 100)
                    "value": get_usage(get_metric(vmInfo['info'], 'limits.memory', 'used'),
                                       get_metric(vmInfo['info'], 'limits.memory', 'hard'))
                }
            ]
        }

        if template:
            return namespaceObjectTemplate

        return cmdbApi('POST', 'object/', cmdb_token, namespaceObjectTemplate)

    extra_disks: str = ''
    if vmInfo['volumes']:
        all_disks = lambda x, y: f"{extra_disks}{x[y]['size']} "
        for ex_disk in range(len(vmInfo['volumes'])):
            extra_disks = all_disks(vmInfo['volumes'], ex_disk)

    sum_disks = lambda x: sum(map(int, x.rstrip().split(' '))) if x else x
    check_public_ip = lambda x, y: y[x]['address'] if x in y else ''
    if 'security_groups' in vmInfo:
        for rule in vmInfo['security_groups']:
            all_ports = tuple(filter(lambda x, y='protocol': x[y] and x[y] != 'icmp' if x[y] else x[y], rule['rules']))
            ingress_ports = tuple(filter(lambda x: x['direction'] == 'ingress' if 'direction' in x else '', all_ports))
            ingress_ports = tuple(map(lambda x: defaultdict(str, x), ingress_ports))
            egress_ports = tuple(filter(lambda x: x['direction'] == 'egress' if 'direction' in x else '', all_ports))
            egress_ports = tuple(map(lambda x: defaultdict(str, x), egress_ports))
    else:
        ingress_ports = egress_ports = ''

    conversion_ports_to_string = lambda x, foo='port_range_max', bar='port_range_min': \
        f"{x['protocol']} {x[foo]}" if x[foo] == x[bar] else f"{x['protocol']} {x[bar]}-{x[foo]}"

    # def getTagName(vmTagIds: list) -> list:
    #     if vmInfo['tag_ids']:
    #         for vmTag in vmTagIds:
    #             for tag in tags:
    #                 vmTagNames = list()
    #                 if tag['id'] == vmTag:
    #                     vmTagNames.append(tag['tag_name'])
    #             return ' \n'.join(vmTagNames)
    #     else:
    #         return ''

    def getTagNames(vmInfo: list) -> list:
        if vmInfo['tag_ids']:
            vmTagNames = list()
            for vmTag in vmInfo['tag_ids']:
                for tag in tags:
                    if tag['id'] == vmTag:
                        vmTagNames.append(tag['tag_name'])
            if len(vmTagNames) == 1:
                return vmTagNames[0]
            return ' \n'.join(vmTagNames)
        else:
            return ''

    checkCreationDate = lambda x: x[:10] if x != None else ''

    vmObjectTemplate: dict = {
        "status": True,
        "type_id": type_id,
        "version": "1.0.0",
        "author_id": author_id,
        "fields": [
            {
                "name": "name",
                "value": vmInfo['service_name']
            },
            {
                "name": "vm-name",
                "value": vmInfo['name']
            },
            {
                "name": "os-type",
                "value": f"{vmInfo['os_name']} {str(vmInfo['os_version'])}"
            },
            {
                "name": "flavor",
                "value": vmInfo['flavor']
            },
            {
                "name": "cpu",
                "value": vmInfo['cpu']
            },
            {
                "name": "ram",
                "value": vmInfo['ram']
            },
            {
                "name": "disk",
                "value": vmInfo['disk']
            },
            {
                "name": "additional-disk",
                "value": sum_disks(extra_disks)
            },
            {
                "name": "summary-vm-info",
                "value": f"{vmInfo['cpu']}/{vmInfo['ram']}/{vmInfo['disk']} \n{'/'.join(extra_disks.rstrip().split())}"
            },
            {
                "name": "local-ip",
                "value": vmInfo['ip']
            },
            {
                "name": "public-ip",
                "value": check_public_ip('public_ip', vmInfo)
            },
            {
                "name": "tags",
                "value": getTagNames(vmInfo)
            },
            {
                "name": "zone",
                "value": vmInfo['region_name']
            },
            {
                "name": "ingress-ports",
                "value": ' \n'.join(tuple(map(conversion_ports_to_string, ingress_ports)))
            },
            {
                "name": "egress-ports",
                "value": ' \n'.join(tuple(map(conversion_ports_to_string, egress_ports)))
            },
            {
                "name": "state",
                "value": vmInfo['state']
            },
            {
                "name": "creator",
                "value": vmInfo['creator_login']
            },
            {
                "name": "vm-id",
                "value": vmInfo['id']
            },
            {
                "name": "os-id",
                "value": vmInfo['openstack_server_id']
            },
            {
                "name": "creation-date",
                "value": checkCreationDate(vmInfo['order_created_at'])
                # "value": lambda x=vmInfo['order_created_at']: x[:10] if x != None else x == ''
            }
        ]
    }
    if method == 'GET_TEMPLATE':
        return vmObjectTemplate

    return cmdbApi(method, 'object/', cmdb_token, vmObjectTemplate)

    # print(response.status_code)
    # print(response.json())
    # try:
    #     return cmdbApi('POST', 'object/', cmdb_token, vmObjectTemplate)
    # except:
    #     number_of_recursions += 1
    #     if response['status_code'] != 201 and number_of_recursions != 5:
    #         time.sleep(1)
    #         print(f"Status Code {response['status_code']}")
    #         put_tag(vmInfo, number_of_recursions)
    #     return dict(vm_name=vmInfo['name'], tag_name=vmInfo['tag_name'], status_code=response['status_code'])


def getCmdbToken() -> str:
    """Function to get app token and user id"""
    from env import cmdb_login, cmdb_password
    authPayload: dict = {
        "user_name": cmdb_login,
        "password": cmdb_password
    }
    # check_cmdb_auth = cmdbApi('GET', 'users/')
    # print(check_cmdb_auth)
    userInfo = cmdbApi('POST', 'auth/login', payload=authPayload)
    return userInfo['token'], userInfo['user']['public_id']


numberOfTread = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)


def getInfoFromAllPage(cmdbItem: str, cmdbToken: str) -> tuple:
    """Function to get different types of cmdb data in one tuple"""
    numbersOfPages = cmdbApi('GET', f"{cmdbItem}/", cmdbToken)['pager']['total_pages']

    def getInfoFromOnePage(pageNumber: int):
        return cmdbApi('GET', f'{cmdbItem}/?page={pageNumber}', cmdbToken)

    fullInfo = list()
    with ThreadPoolExecutor(max_workers=numberOfTread(numbersOfPages)) as executor:
        for pageInfo in executor.map(getInfoFromOnePage, range(1, numbersOfPages + 1)):
            fullInfo.append(pageInfo)
    return tuple(fullInfo)


def create_categorie(name: str, label: str, icon: str, cmdbToken: str, parent: int = None) -> dict:
    """Function to create categories in CMDB"""
    categorieTemplate: dict = {
        "name": name,
        "label": label,
        "meta": {
            "icon": icon,
            "order": None
        },
        "parent": parent,
        "types": []
    }

    return cmdbApi('POST', 'categories/', cmdbToken, categorieTemplate)


def categorie_id(categorieName: str, categorieLabel: str, categorieIcon: str, cmdbToken: str, allCategories: tuple,
                 parentСat: int = None) -> int:
    """Func to create categorie in cmdb"""
    if not any(map(lambda x: any(map(lambda y: y['name'] == categorieName, x['results'])), allCategories)):
        result: dict = create_categorie(categorieName, categorieLabel, categorieIcon, cmdbToken, parentСat)
        return {'public_id': result['raw']['public_id'],
                'name': result['raw']['name'],
                'label': result['raw']['label'],
                'types': result['raw']['types']}
    else:
        result: map = map(lambda x: tuple(filter(lambda y: y['name'] == categorieName, x['results'])), allCategories)
        result: dict = max(max(result))
        return {'public_id': result['public_id'],
                'name': result['name'],
                'label': result['label'],
                'types': result['types']}


def PassportsVM(portalName: str) -> tuple:
    """Main func for create vm objects in datagerry"""

    def portalApi(api_name: str) -> dict:
        """Func for work with Portal REST-API"""
        headers: dict = {
            'user-agent': 'CMDB',
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'authorization': 'Token %s' % portal_info[portalName]['token']}
        response = requests.get('%s%s' % (portal_info[portalName]['url'], api_name), headers=headers, verify=False)
        return dict(stdout=json.loads(response.content), status_code=response.status_code)

    # vmList = portalApi("servers?project_id=e594bc83-938c-48c4-a208-038aedad01de")
    # for i in vmList['stdout']['servers']:
    #     print(i['openstack_server_id'])
    # return


    cmdbToken, userId = getCmdbToken()

    allCategories = getInfoFromAllPage('categories', cmdbToken)

    vmCategorieId = categorie_id('passports', 'Passports VM', 'far fa-folder-open', cmdbToken, allCategories)
    portalCategorieId = categorie_id(portalName, portalName, 'fas fa-folder-open', cmdbToken, allCategories,
                                     vmCategorieId['public_id'])

    cloudDomainsInfo = portalApi('domains')['stdout']
    domainsInfo = dict()
    for domainInfo in cloudDomainsInfo['domains']:
        domainsInfo[domainInfo['id']] = domainInfo['name']
    del cloudDomainsInfo

    for id in domainsInfo:
        if not any(map(lambda x: any(map(lambda y: y['name'] == f'domain_id--{id}', x['results'])), allCategories)):
            create_categorie(f'domain_id--{id}', domainsInfo[id], 'far fa-folder-open', cmdbToken,
                             portalCategorieId['public_id'])
            time.sleep(0.1)

    cloudProjects = portalApi('projects')['stdout']

    def getVcodCheckSum(vcodInfo: dict) -> dict:
        vcod_checksum = portalApi(f"projects/{vcodInfo['id']}/checksum")
        return dict(info=vcodInfo, checksum=hashlib.md5(json.dumps(vcod_checksum['stdout']).encode()).hexdigest())

    def checkSumCloudProjects(cloudProjects: dict) -> dict:

        cloudProjectsWithCheckSum = dict()
        # print(numberOfTread(len(cloudProjects)))
        # with ThreadPoolExecutor(max_workers=numberOfTread(len(cloudProjects))) as executor:
        with ThreadPoolExecutor(max_workers=3) as executor:
            for project in executor.map(getVcodCheckSum, cloudProjects):
                cloudProjectsWithCheckSum[project['info']['name']] = dict(id=project['info']['id'],
                                                                          domain_id=project['info']['domain_id'],
                                                                          zone=project['info']['datacenter_name'],
                                                                          checksum=project['checksum'])
        return cloudProjectsWithCheckSum

    cmdbProjects: tuple = getInfoFromAllPage('types', cmdbToken)

    def deleteAll():
        for deleteCmdbProjects in cmdbProjects:
            for deleteCmdbType in deleteCmdbProjects['results']:
                print('DELETE CMDB TYPE', cmdbApi('DELETE', f"types/{deleteCmdbType['public_id']}", cmdbToken))

        for categories in allCategories:
            for categoriesId in categories['results']:
                print('DELETE CMDB CATEGORIE', cmdbApi('DELETE', f"categories/{categoriesId['public_id']}", cmdbToken))

    allProjects = checkSumCloudProjects(cloudProjects['projects'])
    # from allProjects import allProjects

    del cloudProjects

    cmdbVcodCheckSum = lambda foo: reduce(lambda x, y: x + y, map(lambda bar: tuple(
        map(lambda baz: dict(vcod_id=baz.get('name'), type_id=baz.get('public_id'),
                             check_sum=baz['render_meta']['sections'][0].get('label')), bar['results'])),
                                                                  foo)) if foo else foo

    cmdbVcodCheckSum = cmdbVcodCheckSum(cmdbProjects)
    # from checksum import cmdbVcodCheckSum

    updateCmdbProjects = list()

    for osProject in allProjects:
        for cmdbVcod in cmdbVcodCheckSum:
            if allProjects[osProject]['id'] == cmdbVcod['vcod_id'] and allProjects[osProject]['checksum'] != \
                    cmdbVcod['check_sum']:
                updateCmdbProjects.append(dict(type_id=cmdbVcod['type_id'], vcod_id=cmdbVcod['vcod_id']))

    # print('ALL VCOD', len(cmdbVcodCheckSum))

    #### Delete vcods for update

    # for type_for_delete in updateCmdbProjects:
    # print(portalName, 'UPDATE', type_for_delete)
    # print(cmdbApi('DELETE', f"types/{type_for_delete['type_id']}", cmdbToken))
    # pass

    print('VCOD WHERE WERE CHANGES', len(updateCmdbProjects))

    # all_types_pages = getInfoFromAllPage('categories', cmdbToken)[0]['pager']['total_pages']
    portalTags = portalApi('dict/tags')['stdout']['tags']
    # from tags import portalTags

    for project in allProjects:
        if not any(map(lambda x: any(map(lambda y: y['name'] == allProjects[project]['id'], x['results'])),
                       cmdbProjects)): #and 'gt-mintrud-common-admins-junior' in project:
            # and project in ('gt-foms-prod-jump', 'gt-foms-prod-fortigate'): # cmdbProjects)) and project == 'gt-rosim-dev-customer':

            dataTypeTemplate: dict = {
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
                        "name": "os-type",
                        "label": "os type"
                    },
                    {
                        "type": "text",
                        "name": "flavor",
                        "label": "flavor"
                    },
                    {
                        "type": "text",
                        "name": "cpu",
                        "label": "cpu"
                    },
                    {
                        "type": "text",
                        "name": "ram",
                        "label": "ram"
                    },
                    {
                        "type": "text",
                        "name": "disk",
                        "label": "disk"
                    },
                    {
                        "type": "text",
                        "name": "additional-disk",
                        "label": "additional disk"
                    },
                    {
                        "type": "text",
                        "name": "summary-vm-info",
                        "label": "summary vm info"
                    },
                    {
                        "type": "text",
                        "name": "local-ip",
                        "label": "local ip"
                    },
                    {
                        "type": "text",
                        "name": "public-ip",
                        "label": "public ip"
                    },
                    {
                        "type": "text",
                        "name": "tags",
                        "label": "tags"
                    },
                    {
                        "type": "text",
                        "name": "zone",
                        "label": "zone"
                    },
                    {
                        "type": "text",
                        "name": "ingress-ports",
                        "label": "ingress ports"
                    },
                    {
                        "type": "text",
                        "name": "egress-ports",
                        "label": "egress ports"
                    },

                    {
                        "type": "text",
                        "name": "state",
                        "label": "state"
                    },
                    {
                        "type": "text",
                        "name": "creator",
                        "label": "creator"
                    },
                    {
                        "type": "text",
                        "name": "vm-id",
                        "label": "vm id"
                    },
                    {
                        "type": "text",
                        "name": "os-id",
                        "label": "os id"
                    },
                    {
                        "type": "text",
                        "name": "creation-date",
                        "label": "creation date"
                    }
                ],
                "active": True,
                "version": "1.0.0",
                "author_id": userId,
                "render_meta": {
                    "icon": "fas fa-clipboard-list",
                    "sections": [
                        {
                            "fields": [
                                "name",
                                "vm-name",
                                "os-type",
                                "flavor",
                                "cpu",
                                "ram",
                                "disk",
                                "additional-disk",
                                "summary-vm-info",
                                "local-ip",
                                "public-ip",
                                "tags",
                                "zone",
                                "ingress-ports",
                                "egress-ports",
                                "state",
                                "creator",
                                "vm-id",
                                "os-id",
                                "creation-date"
                            ],
                            "type": "section",
                            "name": allProjects[project]['id'],
                            "label": allProjects[project]['checksum']
                        }
                    ],
                    "externals": [],
                    "summary": {
                        "fields": [
                            "name",
                            "vm-name",
                            "os-type",
                            "flavor",
                            "cpu",
                            "ram",
                            "disk",
                            "additional-disk",
                            "local-ip",
                            "public-ip",
                            "tags",
                            "state",
                            "creation-date"
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
                "name": allProjects[project]['id'],
                "label": f"{project} {allProjects[project]['zone']} {allProjects[project]['id']}",
                "description": f'gt-vcod with id = {allProjects[project]["id"]}'
            }

            create_type = cmdbApi('POST', 'types/', cmdbToken, dataTypeTemplate)
            all_types_pages = getInfoFromAllPage('types', cmdbToken)[0]['pager']['total_pages']
            newAllTypesPages = list()
            for page in range(1, all_types_pages + 1):
                response_page = cmdbApi('GET', f'types/?page={page}', cmdbToken)
                newAllTypesPages.append(response_page)

            # print('ALL_TYPES_PAGES', all_types_pages)
            # all_types_pages = getInfoFromAllPage('types', cmdbToken)
            # print('ALL_TYPES_PAGES', all_types_pages)

            newTypeId = None
            for newTypes in newAllTypesPages:
                for newItem in newTypes['results']:
                    if newItem['name'] == allProjects[project]['id']:
                        newTypeId = newItem['public_id']

            print(newTypeId, 'new type id')

            allCategories: tuple = getInfoFromAllPage('categories', cmdbToken)
            # print(allProjects[project]['domain_id'])
            # print(allCategories)
            findCategory = max(max(map(
                lambda x: tuple(
                    filter(lambda y: y['name'] == f"domain_id--{allProjects[project]['domain_id']}", x['results'])),
                allCategories)))

            print('findCategory', findCategory)

            dataCatTemplate: dict = {
                "public_id": findCategory['public_id'],
                "name": findCategory['name'],
                "label": findCategory['label'],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": portalCategorieId['public_id'],
                "types": findCategory['types']
            }

            if newTypeId == None:
                return

            dataCatTemplate['types'].append(newTypeId)

            put_type_in_catigories = cmdbApi('PUT', f"categories/{findCategory['public_id']}", cmdbToken,
                                              dataCatTemplate)

            print('dataCatTemplate', dataCatTemplate)

            vmList = portalApi(f"servers?project_id={allProjects[project]['id']}")

            for server in vmList['stdout']['servers']:
                time.sleep(0.1)
                try:
                    create_object = objects(server, cmdbToken, newTypeId, userId, tags=portalTags)
                    print('CREATE OBJECT IN %s' % newTypeId, create_object)
                except:
                    time.sleep(5)
                    create_object = objects(server, cmdbToken, newTypeId, userId, tags=portalTags)

    cmdbProjects = getInfoFromAllPage('types', cmdbToken)

    all_cmdb_types_id = reduce(lambda x, y: x + y, map(lambda foo: tuple(
        map(lambda bar: bar.get('public_id'), foo['results'])), cmdbProjects))

    # all_objects = getInfoFromAllPage('objects', cmdbToken)
    # from allObjects import allObjects as all_objects

    # connection_sring = 'mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb'
    # cluster = MongoClient(connection_sring)
    # db = cluster['cmdb']
    # bdObjects = db.get_collection('framework.objects')
    # all_objects = tuple(bdObjects.find({}))

    from allObjects import all_objects

    if not updateCmdbProjects:
        return all_objects
    # updateCmdbProjects = [updateCmdbProjects[0]]
    for cmdbProject in updateCmdbProjects:

        vmList = portalApi(f"servers?project_id={cmdbProject['vcod_id']}")

        cmdbTypeObjects = tuple(filter(lambda x: x['type_id'] == cmdbProject['type_id'], all_objects))

        # cmdbTypeObjects = tuple(filter(lambda f: f['type_id'] == cmdbProject['type_id'],
        #                                  reduce(lambda x, y: x + y, map(lambda z: tuple(
        #                                      map(lambda j: dict(public_id=j.get('public_id'),
        #                                                         type_id=j.get('type_id'),
        #                                                         author_id=j.get('author_id'),
        #                                                         fields=j.get('fields'),
        #                                                         creation_time=j.get('creation_time')),
        #                                          z['results'])), all_objects))))

        # cmdbTypeObjects = tuple(filter(lambda f, k='type_id': f[k] == cmdbProject[k],
        #                                  reduce(lambda x, y: x + y, map(lambda z: tuple(
        #                                      map(lambda j: dict(public_id=j.get('public_id'),
        #                                                         type_id=j.get('type_id'),
        #                                                         author_id=j.get('author_id'),
        #                                                         fields=j.get('fields'),
        #                                                         creation_time=j.get('creation_time')),
        #                                          z['results'])), all_objects))))

        # print(vmList['stdout']['servers'])
        # return

        cloudProjectVm = tuple(map(lambda server: objects(server, 'token', cmdbProject['type_id'], userId,
                                                          'GET_TEMPLATE', tags=portalTags).get('fields'),
                                   vmList['stdout']['servers']))

        for cloudVm in cloudProjectVm:
            if not any(map(lambda x: x['fields'][17]['value'] == cloudVm[17]['value'], cmdbTypeObjects)):
                # print('VM FOR CREATE', cloudVm)
                # time.sleep(0.1)
                objects(cloudVm, cmdbToken, cmdbProject['type_id'], userId, 'POST_NEW_VM', tags=portalTags)

            for cmdb_type in cmdbTypeObjects:

                if cmdb_type['fields'][17]['value'] == cloudVm[17]['value'] and cmdb_type['fields'] != cloudVm:
                    print(f"VM FOR UPDATE in {cmdbProject['type_id']}", cloudVm)

                    # print('###' * 30)
                    # print(int(time.mktime(time.strptime(cmdb_type['creation_time'], '%Y-%m-%dT%H:%M:%S.%f')) * 1000))
                    # print('###' * 30)
                    # unixTime = lambda x: int(time.mktime(time.strptime(x, '%Y-%m-%dT%H:%M:%S.%f')) * 1000) if '.' in x \
                    #     else int(time.mktime(time.strptime(x, '%Y-%m-%dT%H:%M:%S')) * 1000)
                    unixTime = lambda x: int(datetime.datetime.timestamp(x) * 1000)

                    updateObjectTemplate: dict = {
                        "type_id": cmdbProject['type_id'],
                        "status": True,
                        "version": "1.0.1",
                        "creation_time": {
                            # "$date": int(time.mktime(time.strptime(cmdb_type['creation_time'], '%Y-%m-%dT%H:%M:%S.%f')) * 1000)
                            "$date": unixTime(cmdb_type['creation_time'])
                        },
                        "author_id": cmdb_type['author_id'],
                        "last_edit_time": {
                            "$date": int(time.time() * 1000)
                        },
                        "editor_id": userId,
                        "active": True,
                        "fields": cloudVm,
                        "public_id": cmdb_type['public_id'],
                        "views": 0,
                        "comment": ""
                    }

                    time.sleep(0.1)
                    print(objects(updateObjectTemplate, cmdbToken, cmdbProject['type_id'], userId, 'PUT',
                                  tags=portalTags))

        for object in filter(lambda x: x[1][17]['value'] not in map(lambda x: x[17]['value'], cloudProjectVm),
                             map(lambda y: (y.get('public_id'), y.get('fields')), cmdbTypeObjects)):
            print('Delete object', object)
            cmdbApi('DELETE', f"object/{object[0]}", cmdbToken)

        get_info_cmdb_vcod = max(map(lambda x: tuple(
            filter(lambda y: y['name'] == cmdbProject['vcod_id'], x['results'])), cmdbProjects))[0]

        get_info_cmdb_vcod['id'] = get_info_cmdb_vcod['name']

        get_info_cmdb_vcod = getVcodCheckSum(get_info_cmdb_vcod)

        del get_info_cmdb_vcod['info']['id']
        get_info_cmdb_vcod['info']['render_meta']['sections'][0]['label'] = get_info_cmdb_vcod['checksum']
        get_info_cmdb_vcod['info']['last_edit_time'] = \
            time.strftime(f'%Y-%m-%dT%H:%M:%S.{str(time.time())[-5:]}0', time.localtime(time.time()))

        print('####' * 3, 'UPDATE CHECKSUM')
        print(cmdbApi('PUT', f'types/{cmdbProject["type_id"]}', cmdbToken, get_info_cmdb_vcod['info']))

    return all_objects
