#!/usr/bin/python3

import json
import time
import hashlib
import requests
from functools import reduce
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from env import portal_info


def json_read(json_object: dict):
    print(json.dumps(json_object, indent=4))


def cmdb_api(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
    cmdb_api_url: str = "https://cmdb.common.gos-tech.xyz/rest/"
    headers_cmdb_api: dict = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                       data=json.dumps(payload)).content)


def objects(vm_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
            template: bool = False, tags: list = []) -> dict:
    if method == 'PUT':
        return cmdb_api(method, f'object/{vm_info["public_id"]}', cmdb_token, vm_info)

    elif method == 'POST_NEW_VM':

        vm_object_template: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": vm_info
        }

        return cmdb_api('POST', 'object/', cmdb_token, vm_object_template)

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

        # metric = lambda x, y: filter(lambda foo: foo[2][1] if foo[0] == x and foo[1] == y else None, vm_info['info'])

        get_usage = lambda x, y: "%.2f" % ((float(x) / float(y)) * 100) if float(y) != 0.0 else str(float(y))

        fract = lambda x: str(int(x)) if x - int(x) == 0 else "%.2f" % x

        namespace_object_template: dict = {
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
            return namespace_object_template

        return cmdb_api('POST', 'object/', cmdb_token, namespace_object_template)

    extra_disks: str = ''
    if vm_info['volumes']:
        all_disks = lambda x, y: f"{extra_disks}{x[y]['size']} "
        for ex_disk in range(len(vm_info['volumes'])):
            extra_disks = all_disks(vm_info['volumes'], ex_disk)

    sum_disks = lambda x: sum(map(int, x.rstrip().split(' '))) if x else x
    check_public_ip = lambda x, y: y[x]['address'] if x in y else ''
    if 'security_groups' in vm_info:
        for rule in vm_info['security_groups']:
            all_ports = tuple(
                filter(lambda x, y='protocol': x[y] and x[y] != 'icmp' if x[y] else x[y], rule['rules']))
            ingress_ports = tuple(filter(lambda x: x['direction'] == 'ingress', all_ports))
            ingress_ports = tuple(map(lambda x: defaultdict(str, x), ingress_ports))
            egress_ports = tuple(filter(lambda x: x['direction'] == 'egress', all_ports))
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

    vm_object_template: dict = {
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
                "name": "creation-date",
                "value": vm_info['order_created_at'][:10]
            }
        ]
    }
    if method == 'GET_TEMPLATE':
        return vm_object_template

    # print(response.status_code)
    # print(response.json())

    return cmdb_api(method, 'object/', cmdb_token, vm_object_template)
    # try:
    #     return cmdb_api('POST', 'object/', cmdb_token, vm_object_template)
    # except:
    #     number_of_recursions += 1
    #     if response['status_code'] != 201 and number_of_recursions != 5:
    #         time.sleep(1)
    #         print(f"Status Code {response['status_code']}")
    #         put_tag(vm_info, number_of_recursions)
    #     return dict(vm_name=vm_info['name'], tag_name=vm_info['tag_name'], status_code=response['status_code'])


def get_cmdb_token() -> str:
    from env import cmdb_login, cmdb_password
    auth_payload: dict = {
        "user_name": cmdb_login,
        "password": cmdb_password
    }
    # check_cmdb_auth = cmdb_api('GET', 'users/')
    # print(check_cmdb_auth)
    user_info = cmdb_api('POST', 'auth/login', payload=auth_payload)
    return user_info['token'], user_info['user']['public_id']


number_of_tread = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)


def get_info_from_all_page(cmdb_item: str, cmdb_token: str) -> tuple:
    numbers_of_pages = cmdb_api('GET', f"{cmdb_item}/", cmdb_token)['pager']['total_pages']

    def get_info_from_one_page(page_number: int):
        return cmdb_api('GET', f'{cmdb_item}/?page={page_number}', cmdb_token)

    full_info = list()
    with ThreadPoolExecutor(max_workers=number_of_tread(numbers_of_pages)) as executor:
        for page_info in executor.map(get_info_from_one_page, range(1, numbers_of_pages + 1)):
            full_info.append(page_info)
    return tuple(full_info)


def create_categorie(name: str, label: str, icon: str, cmdb_token: str, parent: int = None) -> dict:
    categorie_template: dict = {
        "name": name,
        "label": label,
        "meta": {
            "icon": icon,
            "order": None
        },
        "parent": parent,
        "types": []
    }

    return cmdb_api('POST', 'categories/', cmdb_token, categorie_template)


def categorie_id(categorie_name: str, categorie_label: str, categorie_icon: str, cmdb_token: str, all_categories: tuple,
                 parent_cat: int = None) -> int:
    if not any(map(lambda x: any(map(lambda y: y['name'] == categorie_name, x['results'])), all_categories)):
        result = create_categorie(categorie_name, categorie_label, categorie_icon, cmdb_token, parent_cat)
        return dict(public_id=result['raw']['public_id'], name=result['raw']['name'], label=result['raw']['label'],
                    types=result['raw']['types'])
    else:
        result = max(
            max(map(lambda x: tuple(filter(lambda y: y['name'] == categorie_name, x['results'])), all_categories)))
        return dict(public_id=result['public_id'], name=result['name'], label=result['label'],
                    types=result['types'])


def PassportsVM(portal_name: str) -> tuple:
    def sbercloud_api(api_name: str) -> dict:
        """Func for work with Portal REST-API"""
        headers: dict = {
            'user-agent': 'CMDB',
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'authorization': 'Token %s' % portal_info[portal_name]['token']}
        response = requests.get('%s%s' % (portal_info[portal_name]['url'], api_name), headers=headers, verify=False)
        return dict(stdout=json.loads(response.content), status_code=response.status_code)

    cmdb_token, user_id = get_cmdb_token()

    all_categories = get_info_from_all_page('categories', cmdb_token)

    passports_categorie_id = categorie_id('passports', 'Passports VM', 'far fa-folder-open', cmdb_token, all_categories)
    portal_categorie_id = categorie_id(portal_name, portal_name, 'fas fa-folder-open', cmdb_token, all_categories,
                                       passports_categorie_id['public_id'])
    cloud_domains_info = sbercloud_api('domains')['stdout']

    domains_info = dict()
    for domain_info in cloud_domains_info['domains']:
        domains_info[domain_info['id']] = domain_info['name']
    del cloud_domains_info

    for d_id in domains_info:
        if not any(map(lambda x: any(map(lambda y: y['name'] == f'domain_id--{d_id}', x['results'])), all_categories)):
            create_categorie(f'domain_id--{d_id}', domains_info[d_id], 'far fa-folder-open', cmdb_token,
                             portal_categorie_id['public_id'])
            time.sleep(0.1)

    cloud_projects = sbercloud_api('projects')['stdout']

    def get_vcod_check_sum(vcod_info: dict) -> dict:
        vcod_checksum = sbercloud_api(f"projects/{vcod_info['id']}/checksum")
        return dict(info=vcod_info, checksum=hashlib.md5(json.dumps(vcod_checksum['stdout']).encode()).hexdigest())

    def get_check_sum_cloud_projects(cloud_projects: dict) -> dict:

        cloud_projects_with_check_sum = dict()
        # print(number_of_tread(len(cloud_projects)))
        # with ThreadPoolExecutor(max_workers=number_of_tread(len(cloud_projects))) as executor:
        with ThreadPoolExecutor(max_workers=3) as executor:
            for project in executor.map(get_vcod_check_sum, cloud_projects):
                cloud_projects_with_check_sum[project['info']['name']] = dict(id=project['info']['id'],
                                                                              domain_id=project['info']['domain_id'],
                                                                              zone=project['info']['datacenter_name'],
                                                                              checksum=project['checksum'])
        return cloud_projects_with_check_sum

    all_projects = get_check_sum_cloud_projects(cloud_projects['projects'])

    print(len(all_projects))

    del cloud_projects

    cmdb_projects = get_info_from_all_page('types', cmdb_token)

    cmdb_vcod_check_sum = lambda foo: reduce(lambda x, y: x + y, map(lambda bar: tuple(
        map(lambda baz:
            dict(vcod_id=baz.get('name'),
                 type_id=baz.get('public_id'),
                 check_sum=baz['render_meta']['sections'][0].get('label')), bar['results'])), foo)) if foo else foo

    cmdb_vcod_check_sum = cmdb_vcod_check_sum(cmdb_projects)
    # print(cmdb_vcod_check_sum)
    # return
    # from cmdb_vcod_check_sum import cmdb_vcod_check_sum

    update_cmdb_projects = list()

    for os_project in all_projects:
        for cmdb_vcod in cmdb_vcod_check_sum:
            if all_projects[os_project]['id'] == cmdb_vcod['vcod_id'] and all_projects[os_project]['checksum'] != \
                    cmdb_vcod['check_sum']:
                update_cmdb_projects.append(dict(type_id=cmdb_vcod['type_id'], vcod_id=cmdb_vcod['vcod_id']))

    ###### DELETE ALL
    # for type_for_delete in cmdb_vcod_check_sum:
    #     print(portal_name, 'DELETE', type_for_delete['type_id'])
    #     print(cmdb_api('DELETE', f"types/{type_for_delete['type_id']}", cmdb_token))
    #     time.sleep(0.5)

    # print('ALL VCOD', len(cmdb_vcod_check_sum))

    #### Delete vcods for update

    # for type_for_delete in update_cmdb_projects:
    # print(portal_name, 'UPDATE', type_for_delete)
    # print(cmdb_api('DELETE', f"types/{type_for_delete['type_id']}", cmdb_token))
    # pass

    print('VCOD WHERE WERE CHANGES', len(update_cmdb_projects))

    # all_types_pages = get_info_from_all_page('categories', cmdb_token)[0]['pager']['total_pages']
    portalTags = sbercloud_api('dict/tags')['stdout']['tags']

    for project in all_projects:
        if not any(map(lambda x: any(map(lambda y: y['name'] == all_projects[project]['id'], x['results'])),
                       cmdb_projects)):  # and 'gt-common-admins' in project:
            # and project in ('gt-foms-prod-jump', 'gt-foms-prod-fortigate'): # cmdb_projects)) and project == 'gt-rosim-dev-customer':

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
                        "name": "creation-date",
                        "label": "creation date"
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
                                "creation-date"
                            ],
                            "type": "section",
                            "name": all_projects[project]['id'],
                            "label": all_projects[project]['checksum']
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
                "name": all_projects[project]['id'],
                "label": f"{project} {all_projects[project]['zone']} {all_projects[project]['id']}",
                "description": f'gt-vcod with id = {all_projects[project]["id"]}'
            }

            create_type = cmdb_api('POST', 'types/', cmdb_token, data_type_template)
            all_types_pages = get_info_from_all_page('types', cmdb_token)[0]['pager']['total_pages']
            new_all_types_pages = list()
            for page in range(1, all_types_pages + 1):
                response_page = cmdb_api('GET', f'types/?page={page}', cmdb_token)
                new_all_types_pages.append(response_page)

            new_type_id = None
            for new_types in new_all_types_pages:
                for new_item in new_types['results']:
                    if new_item['name'] == all_projects[project]['id']:
                        new_type_id = new_item['public_id']

            print(new_type_id, 'new type id')

            all_categories = get_info_from_all_page('categories', cmdb_token)
            print(all_projects[project]['domain_id'])
            print(all_categories)
            find_category = max(max(map(
                lambda x: tuple(
                    filter(lambda y: y['name'] == f"domain_id--{all_projects[project]['domain_id']}", x['results'])),
                all_categories)))

            print('find_category', find_category)

            data_cat_template: dict = {
                "public_id": find_category['public_id'],
                "name": find_category['name'],
                "label": find_category['label'],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": portal_categorie_id['public_id'],
                "types": find_category['types']
            }

            if new_type_id == None:
                return

            data_cat_template['types'].append(new_type_id)

            put_type_in_catigories = cmdb_api('PUT', f"categories/{find_category['public_id']}", cmdb_token,
                                              data_cat_template)

            print('data_cat_template', data_cat_template)

            vm_list = sbercloud_api(f"servers?project_id={all_projects[project]['id']}")

            for server in vm_list['stdout']['servers']:
                # print(server)
                time.sleep(0.1)
                try:
                    create_object = objects(server, cmdb_token, new_type_id, user_id, tags=portalTags)
                except:
                    time.sleep(5)
                    create_object = objects(server, cmdb_token, new_type_id, user_id, tags=portalTags)

    cmdb_projects = get_info_from_all_page('types', cmdb_token)

    all_cmdb_types_id = reduce(lambda x, y: x + y, map(lambda foo: tuple(
        map(lambda bar: bar.get('public_id'), foo['results'])), cmdb_projects))

    all_objects = get_info_from_all_page('objects', cmdb_token)

    # from allObjects import allObjects as all_objects

    # print(all_objects)
    # return

    if not update_cmdb_projects:
        return all_objects

    for cmdb_project in update_cmdb_projects:

        vm_list = sbercloud_api(f"servers?project_id={cmdb_project['vcod_id']}")

        cmdb_type_objects = tuple(filter(lambda f, k='type_id': f[k] == cmdb_project[k],
                                         reduce(lambda x, y: x + y, map(lambda z: tuple(
                                             map(lambda j: dict(public_id=j.get('public_id'),
                                                                type_id=j.get('type_id'),
                                                                author_id=j.get('author_id'),
                                                                fields=j.get('fields'),
                                                                creation_time=j.get('creation_time')),
                                                 z['results'])), all_objects))))

        cloud_project_vm = \
            tuple(map(lambda server:
                      objects(server, 'token', cmdb_project['type_id'], user_id, 'GET_TEMPLATE').get('fields'),
                      vm_list['stdout']['servers']))

        for cloud_vm in cloud_project_vm:

            if not any(map(lambda x: x['fields'][16]['value'] == cloud_vm[16]['value'], cmdb_type_objects)):
                print('VM FOR CREATE', cloud_vm)
                time.sleep(0.1)
                print(objects(cloud_vm, cmdb_token, cmdb_project['type_id'], user_id, 'POST_NEW_VM', tags=portalTags))

            for cmdb_type in cmdb_type_objects:

                if cmdb_type['fields'][16]['value'] == cloud_vm[16]['value'] and cmdb_type['fields'] != cloud_vm:
                    print(f"VM FOR UPDATE in {cmdb_project['type_id']}", cloud_vm)

                    # print('###' * 30)
                    # print(int(time.mktime(time.strptime(cmdb_type['creation_time'], '%Y-%m-%dT%H:%M:%S.%f')) * 1000))
                    # print('###' * 30)

                    unixTime = lambda x: int(time.mktime(time.strptime(x, '%Y-%m-%dT%H:%M:%S.%f')) * 1000) if '.' in x \
                        else int(time.mktime(time.strptime(x, '%Y-%m-%dT%H:%M:%S')) * 1000)

                    update_object_template: dict = {
                        "type_id": cmdb_project['type_id'],
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
                        "editor_id": user_id,
                        "active": True,
                        "fields": cloud_vm,
                        "public_id": cmdb_type['public_id'],
                        "views": 0,
                        "comment": ""
                    }

                    time.sleep(0.1)
                    print(objects(update_object_template, cmdb_token, cmdb_project['type_id'], user_id, 'PUT',
                                  tags=portalTags))

        for object in filter(lambda x: x[1][16]['value'] not in map(lambda x: x[16]['value'], cloud_project_vm),
                             map(lambda y: (y.get('public_id'), y.get('fields')), cmdb_type_objects)):
            print('OBJECT for DElete', object)
            print(cmdb_api('DELETE', f"object/{object[0]}", cmdb_token))

        get_info_cmdb_vcod = max(map(lambda x: tuple(
            filter(lambda y: y['name'] == cmdb_project['vcod_id'], x['results'])), cmdb_projects))[0]

        get_info_cmdb_vcod['id'] = get_info_cmdb_vcod['name']

        get_info_cmdb_vcod = get_vcod_check_sum(get_info_cmdb_vcod)

        del get_info_cmdb_vcod['info']['id']
        get_info_cmdb_vcod['info']['render_meta']['sections'][0]['label'] = get_info_cmdb_vcod['checksum']
        get_info_cmdb_vcod['info']['last_edit_time'] = \
            time.strftime(f'%Y-%m-%dT%H:%M:%S.{str(time.time())[-5:]}0', time.localtime(time.time()))

        print('####' * 3, 'UPDATE CHECKSUM')
        print(cmdb_api('PUT', f'types/{cmdb_project["type_id"]}', cmdb_token, get_info_cmdb_vcod['info']))

    return all_objects
