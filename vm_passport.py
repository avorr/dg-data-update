#!/usr/bin/python3
import os
import time
import json
import hashlib
import datetime
from typing import Union, Dict, Any
from tools import *
import requests
from functools import reduce
# from pymongo import MongoClient
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from env import portal_info


def cmdb_api(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
    cmdb_api_url: str = os.environ["DATA_GERRY_CMDB_URL"]
    headers_cmdb_api: dict = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    # response: dict = json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
    #                                              data=json.dumps(payload)).content)
    # if 'types' in api_method:
    #     echo(response)

    # return response
    return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                       data=json.dumps(payload)).content)


def objects(vm_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
            template: bool = False, tags: list = [], vdc_object=None) -> dict:
    if method == 'PUT':
        return cmdb_api(method, f'object/{vm_info["public_id"]}', cmdb_token, vm_info)

    elif method == 'POST_NEW_VM':

        payload_vm_tmp: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": vm_info
        }

        return cmdb_api('POST', 'object/', cmdb_token, payload_vm_tmp)

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
                # else: #### TEST, FIX
                #     return 0 #### TEST, FIX

        # metric = lambda x, y: filter(lambda foo: foo[2][1] if foo[0] == x and foo[1] == y else None, vm_info['info'])

        get_usage = lambda x, y: "%.2f" % ((float(x) / float(y)) * 100) if float(y) != 0.0 else str(float(y))

        fract = lambda x: str(int(x)) if x - int(x) == 0 else "%.2f" % x

        # print('DEBUG')
        # print(vm_info)
        # print('DEBUG')
        payload_ns_tmp: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "namespace",
                    "value": vm_info['namespace']
                },
                {
                    "name": "limits.cpu-hard",
                    "value": get_metric(vm_info['info'], 'limits.cpu', 'hard')
                },
                {
                    "name": "limits.cpu-used",
                    "value": get_metric(vm_info['info'], 'limits.cpu', 'used')
                },
                {
                    "name": "cores-usage",
                    # "value": "%.2f" % ((float(get_metric(vm_info['info'], 'limits.cpu', 'used')) / float(get_metric(vm_info['info'], 'limits.cpu', 'hard'))) * 100)
                    "value": get_usage(get_metric(vm_info['info'], 'limits.cpu', 'used'),
                                       get_metric(vm_info['info'], 'limits.cpu', 'hard'))
                },
                {
                    "name": "limits.memory-hard",
                    "value": fract(convert_to_gb(get_metric(vm_info['info'], 'limits.memory', 'hard')))
                },
                {
                    "name": "limits.memory-used",
                    "value": fract(convert_to_gb(get_metric(vm_info['info'], 'limits.memory', 'used')))
                },
                {
                    "name": "memory-usage",
                    # "value": "%.2f" % ((float(get_metric(vm_info['info'], 'limits.memory', 'used')) / float(get_metric(vm_info['info'], 'limits.memory', 'hard'))) * 100)
                    "value": get_usage(get_metric(vm_info['info'], 'limits.memory', 'used'),
                                       get_metric(vm_info['info'], 'limits.memory', 'hard'))
                }
            ]
        }

        if template:
            return payload_ns_tmp

        return cmdb_api('POST', 'object/', cmdb_token, payload_ns_tmp)

    extra_disks: str = ''
    if vm_info['volumes']:
        all_disks = lambda x, y: f"{extra_disks}{x[y]['size']} "
        for ex_disk in range(len(vm_info['volumes'])):
            extra_disks = all_disks(vm_info['volumes'], ex_disk)

    sum_disks = lambda x: sum(map(int, x.rstrip().split(' '))) if x else x
    check_public_ip = lambda x, y: y[x]['address'] if x in y else ''
    if 'security_groups' in vm_info:
        for rule in vm_info['security_groups']:
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
    #     if vm_info['tag_ids']:
    #         for vmTag in vmTagIds:
    #             for tag in tags:
    #                 vmTagNames = list()
    #                 if tag['id'] == vmTag:
    #                     vmTagNames.append(tag['tag_name'])
    #             return ' \n'.join(vmTagNames)
    #     else:
    #         return ''

    def getTagNames(vm_info: list) -> list:
        if vm_info['tag_ids']:
            vmTagNames = list()
            for vmTag in vm_info['tag_ids']:
                for tag in tags:
                    if tag['id'] == vmTag:
                        vmTagNames.append(tag['tag_name'])
            if len(vmTagNames) == 1:
                return vmTagNames[0]
            return ' \n'.join(vmTagNames)
        else:
            return ''

    checkCreationDate = lambda x: x[:10] if x != None else ''

    payload_vm_tmp: dict = {
        "status": True,
        "type_id": type_id,
        "version": "1.0.0",
        "author_id": author_id,
        "fields": [
            {
                "name": "name",
                "value": vm_info['service_name']
            },
            {
                "name": "vm-name",
                "value": vm_info['name']
            },
            {
                "name": "os-type",
                "value": f"{vm_info['os_name']} {str(vm_info['os_version'])}"
            },
            {
                "name": "flavor",
                "value": vm_info['flavor']
            },
            {
                "name": "cpu",
                "value": vm_info['cpu']
            },
            {
                "name": "ram",
                "value": vm_info['ram']
            },
            {
                "name": "disk",
                "value": vm_info['disk']
            },
            {
                "name": "additional-disk",
                "value": sum_disks(extra_disks)
            },
            {
                "name": "summary-vm-info",
                "value": f"{vm_info['cpu']}/{vm_info['ram']}/{vm_info['disk']} \n{'/'.join(extra_disks.rstrip().split())}"
            },
            {
                "name": "local-ip",
                "value": vm_info['ip']
            },
            {
                "name": "public-ip",
                "value": check_public_ip('public_ip', vm_info)
            },
            {
                "name": "tags",
                "value": getTagNames(vm_info)
            },
            {
                "name": "zone",
                "value": vm_info['region_name']
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
                "value": vm_info['state']
            },
            {
                "name": "creator",
                "value": vm_info['creator_login']
            },
            {
                "name": "vm-id",
                "value": vm_info['id']
            },
            {
                "name": "os-id",
                "value": vm_info['openstack_server_id']
            },
            {
                "name": "creation-date",
                "value": checkCreationDate(vm_info['order_created_at'])
                # "value": lambda x=vm_info['order_created_at']: x[:10] if x != None else x == ''
            },
            {
                "name": "vdc-link",
                "value": vdc_object
            }
        ]
    }
    if method == 'GET_TEMPLATE':
        return payload_vm_tmp

    return cmdb_api(method, 'object/', cmdb_token, payload_vm_tmp)

    # print(response.status_code)
    # print(response.json())
    # try:
    #     return cmdb_api('POST', 'object/', cmdb_token, payload_vm_tmp)
    # except:
    #     number_of_recursions += 1
    #     if response['status_code'] != 201 and number_of_recursions != 5:
    #         time.sleep(1)
    #         print(f"Status Code {response['status_code']}")
    #         put_tag(vm_info, number_of_recursions)
    #     return dict(vm_name=vm_info['name'], tag_name=vm_info['tag_name'], status_code=response['status_code'])


def getCmdbToken() -> str:
    """Function to get app token and user id"""
    from env import cmdb_login, cmdb_password
    payload_auth: dict = {
        "user_name": cmdb_login,
        "password": cmdb_password
    }
    # check_cmdb_auth = cmdb_api('GET', 'users/')
    # print(check_cmdb_auth)
    user_info = cmdb_api('POST', 'auth/login', payload=payload_auth)
    return user_info['token'], user_info['user']['public_id']


thread_count = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)


def getInfoFromAllPage(dg_item: str, cmdb_token: str) -> tuple:
    """Function to get different types of cmdb data in one tuple"""
    json_count = cmdb_api('GET', f"{dg_item}/", cmdb_token)['pager']['total_pages']

    def getInfoFromOnePage(page_number: int):
        return cmdb_api('GET', f'{dg_item}/?page={page_number}', cmdb_token)

    full_info = list()
    with ThreadPoolExecutor(max_workers=thread_count(json_count)) as executor:
        for page_info in executor.map(getInfoFromOnePage, range(1, json_count + 1)):
            full_info.append(page_info)
    return tuple(full_info)


def create_categorie(name: str, label: str, icon: str, cmdb_token: str, parent: int = None) -> dict:
    """Function to create categories in CMDB"""
    payload_categorie_tmp: dict = {
        "name": name,
        "label": label,
        "meta": {
            "icon": icon,
            "order": None
        },
        "parent": parent,
        "types": []
    }

    return cmdb_api('POST', 'categories/', cmdb_token, payload_categorie_tmp)


def categorie_id(categorie_name: str, categorie_label: str, categorie_icon: str, cmdb_token: str, dg_categories: tuple,
                 parent_categorie: int = None) -> dict:  # Union[dict[str, Any], dict[str, Any]]:
    """Func to create categorie in cmdb"""
    if not any(map(lambda x: any(map(lambda y: y['name'] == categorie_name, x['results'])), dg_categories)):
        result: dict = create_categorie(categorie_name, categorie_label, categorie_icon, cmdb_token, parent_categorie)
        return {
            'public_id': result['raw']['public_id'],
            'name': result['raw']['name'],
            'label': result['raw']['label'],
            'types': result['raw']['types']
        }
    else:
        result: map = map(lambda x: tuple(filter(lambda y: y['name'] == categorie_name, x['results'])), dg_categories)
        result: dict = max(max(result))
        return {
            'public_id': result['public_id'],
            'name': result['name'],
            'label': result['label'],
            'types': result['types']
        }


def portal_api(api_name: str, portal_name: str) -> dict:
    """Func for work with Portal REST-API"""
    headers: dict = {
        'user-agent': 'CMDB',
        'Content-type': 'application/json',
        'Accept': 'text/plain',
        'authorization': 'Token %s' % portal_info[portal_name]['token']}
    response = requests.get('%s%s' % (portal_info[portal_name]['url'], api_name), headers=headers, verify=False)
    return dict(stdout=json.loads(response.content), status_code=response.status_code)


def get_mongodb_objects(collection: str) -> tuple:
    mongo_db = MongoClient('mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb')['cmdb']
    # mongo_db = MongoClient('mongodb://172.26.107.101:30039/cmdb')['cmdb']
    # mongo_objects = mongo_db.get_collection('framework.%s' % collection)
    mongo_objects = mongo_db.get_collection(collection)
    return tuple(mongo_objects.find())


def PassportsVM(portal_name: str) -> tuple:
    """Main func for create vm objects in datagerry"""

    # vm_list = portal_api("servers?project_id=e594bc83-938c-48c4-a208-038aedad01de")
    # for i in vm_list['stdout']['servers']:
    #     print(i['openstack_server_id'])
    # return

    def get_mongodb_objects(collection: str) -> tuple:
        mongo_db = MongoClient('mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb')['cmdb']
        # mongo_db = MongoClient('mongodb://172.26.107.101:30039/cmdb')['cmdb']
        # mongo_objects = mongo_db.get_collection('framework.%s' % collection)
        mongo_objects = mongo_db.get_collection(collection)
        return tuple(mongo_objects.find())

    cmdb_token, user_id = getCmdbToken()

    dg_categories = getInfoFromAllPage('categories', cmdb_token)

    vm_category_id = categorie_id('passports', 'Passports VM', 'far fa-folder-open', cmdb_token, dg_categories)
    portal_category_id = categorie_id(portal_name, portal_name, 'fas fa-folder-open', cmdb_token, dg_categories,
                                      vm_category_id['public_id'])
    # vdc_category_id = categorie_id('passports-vdc', 'Passports VDC', 'fas fa-network-wired', cmdb_token, dg_categories)

    portal_domains_info: dict = portal_api('domains', portal_name)['stdout']
    # json_read(portal_domains_info)

    domains_info: dict = {domain['id']: domain['name'] for domain in portal_domains_info['domains']}

    # domains_info = dict()
    # for domainInfo in portal_domains_info['domains']:
    #     domains_info[domainInfo['id']] = domainInfo['name']
    # del portal_domains_info

    for id in domains_info:
        if not any(map(lambda x: any(map(lambda y: y['name'] == f'domain_id--{id}', x['results'])), dg_categories)):
            create_categorie(f'domain_id--{id}', domains_info[id], 'far fa-folder-open', cmdb_token,
                             portal_category_id['public_id'])

    portal_projects: dict = portal_api('projects', portal_name)['stdout']

    def get_project_checksum(vdc_info: dict) -> dict:
        vdc_checksum = portal_api(f"projects/{vdc_info['id']}/checksum", portal_name)
        return dict(info=vdc_info, checksum=hashlib.md5(json.dumps(vdc_checksum['stdout']).encode()).hexdigest())

    def checksum_vdcs(cloud_projects: dict) -> dict:
        checksum_portal_vdcs = dict()
        # print(thread_count(len(cloud_projects)))
        # with ThreadPoolExecutor(max_workers=thread_count(len(cloud_projects))) as executor:
        with ThreadPoolExecutor(max_workers=3) as executor:
            for project in executor.map(get_project_checksum, cloud_projects):
                checksum_portal_vdcs[project['info']['name']] = dict(id=project['info']['id'],
                                                                     domain_id=project['info']['domain_id'],
                                                                     zone=project['info']['datacenter_name'],
                                                                     checksum=project['checksum'])
        return checksum_portal_vdcs

    dg_types: tuple = get_mongodb_objects('framework.types')

    def delete_all():
        for deleteCmdbType in dg_types:
            # print(deleteCmdbType['label'])
            # if deleteCmdbType['public_id'] in list(range(171, 262)):
            # if deleteCmdbType['description'] == 'passport-vm-%s' % portal_name:
            # if 'pd20-' in deleteCmdbType['label']:
                # print('del', deleteCmdbType['label'])
            print('DELETE CMDB TYPE', cmdb_api('DELETE', f"types/{deleteCmdbType['public_id']}", cmdb_token))

        for categories in dg_categories:
            for categoriesId in categories['results']:
                print('DELETE CMDB CATEGORIE', cmdb_api('DELETE', f"categories/{categoriesId['public_id']}", cmdb_token))


    # dg_types: tuple = getInfoFromAllPage('types', cmdb_token)


    # {'vdc_id': 'os-cluster-PD15--ocp_prod_foms_tech', 'type_id': 86, 'check_sum': 'ocp.prod.foms.tech'}

    # dg_vdc_checksum = \
    #     map(lambda x: dict(vdc_id=x.get('name'), type_id=x.get('public_id'),
    #                        check_sum=x['render_meta']['sections'][0].get('label')), dg_types)
    # x['description'] == 'passport-vm-%s' % portal_name else x, dg_types)



    # get_vdc_checksum = lambda foo: reduce(lambda x, y: x + y, map(lambda bar: tuple(
    #     map(lambda baz: dict(vdc_id=baz.get('name'), type_id=baz.get('public_id'),
    #                          check_sum=baz['render_meta']['sections'][0].get('label')), bar['results'])),
    #                                                               foo)) if foo else foo

    # dg_vdc_checksum = get_vdc_checksum(dg_types)
    # print(dg_vdc_checksum)
    # return

    vm_projects = list()
    for vm_type in dg_types:
        if vm_type['description'] == 'passport-vm-%s' % portal_name:
            vm_projects.append(vm_type)

    vm_projects_ids = tuple(map(lambda x: x['name'], vm_projects))

    from vdcPassports import PassportsVDC
    all_vdc_objects, dg_vdc_type = PassportsVDC(portal_name)
    # print(list(map(lambda x: x['fields'][5]['value'], all_vdc_objects)))
    # return

    project_id_vcd_types = dict()

    for project in portal_projects['projects']:
        # print(project['id'])
        # if project['id'] in ('803aa26d-5e77-42bd-8320-88056f09690e', '148d5303-579d-48f3-a54e-c8dea68b8e55'):
        #     print(project)
        # for vm_project in vm_projects:
        for vdc_vm in all_vdc_objects:
            if vdc_vm['fields'][5]['value'] == project['id']:  # and vdc_vm['fields'][5]['value'] == vm_project['name']:
                project_id_vcd_types[project['id']] = {'vdc_object_id': vdc_vm['public_id']}

                # {'vm_project_id': vm_project['public_id'],
            # if project['id'] not in vm_projects_ids:
            # print(True, project['id'])
            # project_id_vcd_types[project['id']] = {'vdc_object_id': vdc_vm['public_id']}
        # {'vm_project_id': None,

    # json_read(project_id_vcd_types)
    # return

    allProjects = checksum_vdcs(portal_projects['projects'])
    # from allProjects import allProjects

    del portal_projects

    # get_vdc_checksum = lambda foo: reduce(lambda x, y: x + y, map(lambda bar: tuple(
    #     map(lambda baz: dict(vdc_id=baz.get('name'), type_id=baz.get('public_id'),
    #                          check_sum=baz['render_meta']['sections'][0].get('label')), bar['results'])),
    #                                                               foo)) if foo else foo

    # dg_vdc_checksum = get_vdc_checksum(dg_types)


    dg_vdc_checksum = tuple(map(lambda x: dict(vdc_id=x.get('name'), type_id=x.get('public_id'),
                           check_sum=x['render_meta']['sections'][0].get('label')), dg_types))
    # from checksum import dg_vdc_checksum

    update_dg_types = list()

    for osProject in allProjects:
        for cmdbVcod in dg_vdc_checksum:
            if allProjects[osProject]['id'] == cmdbVcod['vdc_id'] and allProjects[osProject]['checksum'] != \
                    cmdbVcod['check_sum']:
                update_dg_types.append(dict(type_id=cmdbVcod['type_id'], vdc_id=cmdbVcod['vdc_id']))
            # for vdc_vm in all_vdc_objects:
            # print(cmdbVcod['vdc_id'])
            # print(vdc_vm['fields'][5]['value'])
            # print(vdc_vm['fields'])
            # print(cmdbVcod)
            # print('#######################')
            # if vdc_vm['fields'][5]['value'] == cmdbVcod['vdc_id']:
            #         project_id_vcd_types[cmdbVcod['type_id']] = vdc_vm['public_id']

    # print('ALL VCOD', len(dg_vdc_checksum))

    #### Delete vcods for update

    # for type_for_delete in update_dg_types:
    # print(portal_name, 'UPDATE', type_for_delete)
    # print(cmdb_api('DELETE', f"types/{type_for_delete['type_id']}", cmdb_token))
    # pass

    print('VCOD WHERE WERE CHANGES', len(update_dg_types))


    # all_types_pages = getInfoFromAllPage('categories', cmdb_token)[0]['pager']['total_pages']
    portal_tags = portal_api('dict/tags', portal_name)['stdout']['tags']
    # from tags import portal_tags
    # from allObjects import all_objects
    # from vm_passport import get_mongodb_objects
    all_objects = get_mongodb_objects('framework.objects')

    # for project in allProjects:
    #     if not any(map(lambda x: any(map(lambda y: y['name'] == allProjects[project]['id'], x['results'])), dg_types)):
    for project in allProjects:
        if not any(map(lambda x: x['name'] == allProjects[project]['id'], dg_types)):

            # print(allProjects[project]['id'])
            vdc_id = project_id_vcd_types[allProjects[project]['id']]['vdc_object_id']
            # json_read(project_id_vcd_types)
            # print(vdc_id)

            # print(project)
            # print(project['id'])
            # print(project_id_vcd_types[project['name']])

            # and 'gt-mintrud-common-admins-junior' in project:
            # and project in ('gt-foms-prod-jump', 'gt-foms-prod-fortigate'): # dg_types)) and project == 'gt-rosim-dev-customer':

            payload_type_tmp: dict = {
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
                    },
                    {
                        "type": "ref",
                        "name": "vdc-link",
                        "label": "vdc link",
                        "ref_types": [
                            dg_vdc_type['public_id']
                        ],
                        "summaries": [],
                        "default": len(all_objects)
                    }
                ],
                "active": True,
                "version": "1.0.0",
                "author_id": user_id,
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
                                "creation-date",
                                "vdc-link"
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
                "label": f"{project} | {allProjects[project]['zone']} | {allProjects[project]['id']}",
                "description": f'passport-vm-{portal_name}'
            }

            create_type = cmdb_api('POST', 'types/', cmdb_token, payload_type_tmp)
            print(create_type, 'create_type')

            print(create_type['result_id'], 'new type id')

            from vm_passport import get_mongodb_objects
            dg_categories: tuple = get_mongodb_objects('framework.categories')

            category_search: dict = \
                max(filter(lambda y: y['name'] == f"domain_id--{allProjects[project]['domain_id']}", dg_categories))

            # dg_categories: tuple = getInfoFromAllPage('categories', cmdb_token)
            # category_search = max(max(map(lambda x: tuple(
            #     filter(lambda y: y['name'] == f"domain_id--{allProjects[project]['domain_id']}", x['results'])),
            #                               dg_categories)))

            # print(category_search)
            # print(type(category_search))
            # print('api category_search')

            payload_categorie_tmp: dict = {
                "public_id": category_search['public_id'],
                "name": category_search['name'],
                "label": category_search['label'],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": portal_category_id['public_id'],
                "types": category_search['types']
            }

            payload_categorie_tmp['types'].append(create_type['result_id'])

            cmdb_api('PUT', f"categories/{category_search['public_id']}", cmdb_token, payload_categorie_tmp)

            print('payload_categorie_tmp', payload_categorie_tmp)

            vm_list: dict = portal_api(f"servers?project_id={allProjects[project]['id']}", portal_name)

            for server in vm_list['stdout']['servers']:
                time.sleep(0.1)
                try:
                    create_object = objects(server, cmdb_token, create_type['result_id'], user_id, tags=portal_tags,
                                            vdc_object=vdc_id)
                    print('CREATE OBJECT IN %s' % create_type['result_id'], create_object)
                except:
                    time.sleep(5)
                    objects(server, cmdb_token, create_type['result_id'], user_id, tags=portal_tags, vdc_object=vdc_id)

    # return
    # dg_types = getInfoFromAllPage('types', cmdb_token)

    # all_cmdb_types_id = reduce(lambda x, y: x + y, map(lambda foo: tuple(
    #     map(lambda bar: bar.get('public_id'), foo['results'])), dg_types))

    # all_objects = getInfoFromAllPage('objects', cmdb_token)
    # from allObjects import allObjects as all_objects

    # connection_sring = 'mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb'
    # cluster = MongoClient(connection_sring)
    # db = cluster['cmdb']
    # bdObjects = db.get_collection('framework.objects')
    # all_objects = tuple(bdObjects.find({}))

    # from allObjects import all_objects
    # from vm_passport import get_mongodb_objects
    # all_objects = get_mongodb_objects('framework.objects')

    if not update_dg_types:
        return all_objects
    # update_dg_types = [update_dg_types[0]]
    for cmdbProject in update_dg_types:
        vdc_id = project_id_vcd_types[cmdbProject['vdc_id']]['vdc_object_id']
        # print(vdc_id)

        vm_list = portal_api(f"servers?project_id={cmdbProject['vdc_id']}", portal_name)

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

        # print(vm_list['stdout']['servers'])
        # return

        cloudProjectVm = tuple(map(lambda server: objects(server, 'token', cmdbProject['type_id'], user_id,
                                                          'GET_TEMPLATE', tags=portal_tags, vdc_object=vdc_id).get('fields'),
                                   vm_list['stdout']['servers']))

        for cloudVm in cloudProjectVm:
            if not any(map(lambda x: x['fields'][17]['value'] == cloudVm[17]['value'], cmdbTypeObjects)):
                # print('VM FOR CREATE', cloudVm)
                # time.sleep(0.1)
                objects(cloudVm, cmdb_token, cmdbProject['type_id'], user_id, 'POST_NEW_VM', tags=portal_tags, 
                        vdc_object=vdc_id)

            for cmdb_type in cmdbTypeObjects:

                if cmdb_type['fields'][17]['value'] == cloudVm[17]['value'] and cmdb_type['fields'] != cloudVm:
                    print(f"VM FOR UPDATE IN {cmdbProject['type_id']}", cloudVm)

                    # print('###' * 30)
                    # print(int(time.mktime(time.strptime(cmdb_type['creation_time'], '%Y-%m-%dT%H:%M:%S.%f')) * 1000))
                    # print('###' * 30)
                    # unixTime = lambda x: int(time.mktime(time.strptime(x, '%Y-%m-%dT%H:%M:%S.%f')) * 1000) if '.' in x \
                    #     else int(time.mktime(time.strptime(x, '%Y-%m-%dT%H:%M:%S')) * 1000)

                    unixTime = lambda x: int(datetime.datetime.timestamp(x) * 1000)


                    payload_object_tmp: dict = {
                        "type_id": cmdbProject['type_id'],
                        "status": True,
                        "version": "1.0.1",
                        "creation_time": {
                            # "$date": int(time.mktime(time.strptime(cmdb_type['creation_time'], '%Y-%m-%dT%H:%M:%S.%f')) * 1000)
                            # "$date": unixTime(cmdb_type['creation_time'])
                            "$date": int(datetime.datetime.timestamp(cmdb_type['creation_time']) * 1000)
                        },
                        "author_id": cmdb_type['author_id'],
                        "last_edit_time": {
                            "$date": int(time.time() * 1000)
                        },
                        "editor_id": user_id,
                        "active": True,
                        "fields": cloudVm,
                        "public_id": cmdb_type['public_id'],
                        "views": 0,
                        "comment": ""
                    }

                    time.sleep(0.1)
                    print(objects(payload_object_tmp, cmdb_token, cmdbProject['type_id'], user_id, 'PUT',
                                  tags=portal_tags, vdc_object=vdc_id))

        for object in filter(lambda x: x[1][17]['value'] not in map(lambda x: x[17]['value'], cloudProjectVm),
                             map(lambda y: (y.get('public_id'), y.get('fields')), cmdbTypeObjects)):
            print('Delete object', object)
            cmdb_api('DELETE', f"object/{object[0]}", cmdb_token)

        # get_info_cmdb_vdc = max(map(lambda x: tuple(
        #     filter(lambda y: y['name'] == cmdbProject['vdc_id'], x['results'])), dg_types))[0]
        get_info_cmdb_vdc = max(filter(lambda y: y['name'] == cmdbProject['vdc_id'], dg_types))

        get_info_cmdb_vdc['id'] = get_info_cmdb_vdc['name']

        get_info_cmdb_vdc = get_project_checksum(get_info_cmdb_vdc)

        del get_info_cmdb_vdc['info']['id']
        get_info_cmdb_vdc['info']['render_meta']['sections'][0]['label'] = get_info_cmdb_vdc['checksum']
        get_info_cmdb_vdc['info']['last_edit_time'] = \
            time.strftime(f'%Y-%m-%dT%H:%M:%S.{str(time.time())[-5:]}0', time.localtime(time.time()))

        print('####' * 3, 'UPDATE CHECKSUM')
        print(cmdb_api('PUT', f'types/{cmdbProject["type_id"]}', cmdb_token, get_info_cmdb_vdc['info']))
        # return

    return all_objects
