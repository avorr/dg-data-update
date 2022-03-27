#!/usr/bin/python3
import os
import time
import hashlib
import requests
import datetime
from datetime import datetime, date
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from tools import *
from env import portal_info

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def cmdb_api(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
    """
    Func to use DataGerry rest-api
    :param method:
    :param api_method:
    :param token:
    :param payload:
    :return:
    """
    cmdb_api_url: str = os.environ["DATA_GERRY_CMDB_URL"]
    headers_cmdb_api: dict = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                       data=json.dumps(payload)).content)


def objects(vm_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
            template: bool = False, tags: list = [], vdc_object=None) -> dict:
    """
    Func to create or update or delete objects in DataGerry
    :param vm_info:
    :param cmdb_token:
    :param type_id:
    :param author_id:
    :param method:
    :param template:
    :param tags:
    :param vdc_object:
    :return:
    """
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

        # metric = lambda x, y: filter(lambda foo: foo[2][1] if foo[0] == x and foo[1] == y else None, vm_info['info'])

        get_usage = lambda x, y: "%.2f" % ((float(x) / float(y)) * 100) if float(y) != 0.0 else str(float(y))

        fract = lambda x: str(int(x)) if x - int(x) == 0 else "%.2f" % x

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

    def get_tag_name(vm_info: list) -> str:
        """
        Func to get tag from server json
        :param vm_info:
        :return:
        """
        if vm_info['tag_ids']:
            vm_tag_names = list()
            for vmTag in vm_info['tag_ids']:
                for tag in tags:
                    if tag['id'] == vmTag:
                        vm_tag_names.append(tag['tag_name'])
            if len(vm_tag_names) == 1:
                return vm_tag_names[0]
            return ' \n'.join(vm_tag_names)
        else:
            return ''

    check_creation_date = lambda x: x[:10] if x != None else ''

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
                "value": get_tag_name(vm_info)
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
                "value": check_creation_date(vm_info['order_created_at'])
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


def get_dg_token() -> str:
    """
    Function to get app token and user id
    :return:
    """
    from env import cmdb_login, cmdb_password
    payload_auth: dict = {
        "user_name": cmdb_login,
        "password": cmdb_password
    }
    user_info = cmdb_api('POST', 'auth/login', payload=payload_auth)
    return user_info['token'], user_info['user']['public_id']


thread_count = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)


def get_all_jsons(dg_item: str, cmdb_token: str) -> tuple:
    """
    Function to get different types of cmdb data in one tuple
    :param dg_item:
    :param cmdb_token:
    :return:
    """
    json_count = cmdb_api('GET', f"{dg_item}/", cmdb_token)['pager']['total_pages']

    def get_one_json(page_number: int):
        return cmdb_api('GET', f'{dg_item}/?page={page_number}', cmdb_token)

    full_info = list()
    # with ThreadPoolExecutor(max_workers=thread_count(json_count)) as executor:
    with ThreadPoolExecutor(max_workers=1) as executor:
        for page_info in executor.map(get_one_json, range(1, json_count + 1)):
            full_info.append(page_info)
    return tuple(full_info)


def create_category(name: str, label: str, icon: str, cmdb_token: str, parent: int = None) -> dict:
    """
    Function to create categories in CMDB
    :param name:
    :param label:
    :param icon:
    :param cmdb_token:
    :param parent:
    :return:
    """
    payload_category_tmp: dict = {
        "name": name,
        "label": label,
        "meta": {
            "icon": icon,
            "order": None
        },
        "parent": parent,
        "types": list()
    }

    return cmdb_api('POST', 'categories/', cmdb_token, payload_category_tmp)


def category_id(category_name: str, category_label: str, category_icon: str, cmdb_token: str, dg_categories: tuple,
                parent_category: int = None) -> dict:
    """
    Func to create category in cmdb
    :param category_name:
    :param category_label:
    :param category_icon:
    :param cmdb_token:
    :param dg_categories:
    :param parent_category:
    :return:
    """

    if not any(map(lambda y: y['name'] == category_name, dg_categories)):
        print(True)
        result: dict = create_category(category_name, category_label, category_icon, cmdb_token, parent_category)
        return {
            'public_id': result['raw']['public_id'],
            'name': result['raw']['name'],
            'label': result['raw']['label'],
            'types': result['raw']['types']
        }
    else:
        result: dict = max(filter(lambda y: y['name'] == category_name, dg_categories))
        return {
            'public_id': result['public_id'],
            'name': result['name'],
            'label': result['label'],
            'types': result['types']
        }


def portal_api(api_name: str, portal_name: str) -> dict:
    """
    Func to work with Portal REST-API
    :param api_name:
    :param portal_name:
    :return: dict
    """
    headers: dict = {
        'user-agent': 'CMDB',
        'Content-type': 'application/json',
        'Accept': 'text/plain',
        'authorization': 'Token %s' % portal_info[portal_name]['token']
    }
    response = requests.get('%s/api/v1/%s' % (portal_info[portal_name]['url'], api_name), headers=headers, verify=False)
    return dict(stdout=json.loads(response.content), status_code=response.status_code)


def get_mongodb_objects(collection: str, find: dict = None) -> tuple:
    """
    Func to work with DataGerry mongodb
    :param collection:
    :param find:
    :return:
    """
    mongo_db = MongoClient('mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb')['cmdb']
    # mongo_db = MongoClient('mongodb://172.26.107.101:30039/cmdb')['cmdb']
    # mongo_objects = mongo_db.get_collection('framework.%s' % collection)
    mongo_objects = mongo_db.get_collection(collection)
    if find:
        # mongo_objects = mongo_db.get_collection(collection)
        return tuple(mongo_objects.find(find))
    # mongo_objects = mongo_db.get_collection(collection)
    return tuple(mongo_objects.find())


def json_serial(obj: datetime) -> str:
    """
    JSON serializer for objects not serializable by default json code
    :param obj: datetime
    :return: str
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def PassportsVM(portal_name: str) -> tuple:
    """
    Main func for create vm objects in DataGerry
    :param portal_name: ex: PD15
    :return: tuple
    """
    cmdb_token, user_id = get_dg_token()

    dg_categories: tuple = get_mongodb_objects('framework.categories')

    vm_category_id: dict = category_id('passports', 'Passports VM', 'far fa-folder-open', cmdb_token, dg_categories)
    portal_category_id: dict = \
        category_id(portal_name, portal_name, 'fas fa-folder-open', cmdb_token, dg_categories,
                    vm_category_id['public_id'])

    # vdc_category_id = category_id('passports-vdc', 'Passports VDC', 'fas fa-network-wired', cmdb_token, dg_categories)

    portal_domains_info: dict = portal_api('domains', portal_name)['stdout']

    domains_info: dict = {
        domain['id']: domain['name'] for domain in portal_domains_info['domains']
    }

    for domain_id in domains_info:
        if not any(map(lambda y: y['name'] == 'domain_id--%s' % domain_id, dg_categories)):
            create_category('domain_id--%s' % domain_id, domains_info[domain_id], 'far fa-folder-open', cmdb_token,
                            portal_category_id['public_id'])

    portal_groups_info: dict = portal_api('groups', portal_name)['stdout']

    for group_id in portal_groups_info['groups']:
        if not any(map(lambda y: y['name'] == 'group_id--%s' % group_id['id'], dg_categories)):
            for domain in dg_categories:
                if domain['name'] == 'domain_id--%s' % group_id['domain_id']:
                    create_category("group_id--%s" % group_id['id'], group_id['name'],
                                    'fas fa-folder-open', cmdb_token, domain['public_id'])

    portal_projects: dict = portal_api('projects', portal_name)['stdout']

    def get_vdc_checksum(vdc_info: dict) -> dict:
        """
        Func to get vdc checksum from portal
        :param vdc_info:
        :return:
        """
        # vdc_checksum = portal_api(f"projects/{vdc_info['id']}/checksum", portal_name)
        vdc_checksum: dict = portal_api(f"servers?project_id=%s" % vdc_info['id'], portal_name)
        return dict(info=vdc_info, checksum=hashlib.md5(json.dumps(vdc_checksum['stdout']).encode()).hexdigest())

    def checksum_vdc(cloud_projects: dict) -> dict:
        """
        Func to get vdc checksum from portal
        :param cloud_projects:
        :return:
        """
        checksum_portal_vdc = dict()
        # with ThreadPoolExecutor(max_workers=thread_count(len(cloud_projects))) as executor:
        with ThreadPoolExecutor(max_workers=4) as executor:
            for project in executor.map(get_vdc_checksum, cloud_projects):
                checksum_portal_vdc[project['info']['name']] = {
                    'id': project['info']['id'],
                    'domain_id': project['info']['domain_id'],
                    'group_id': project['info']['group_id'],
                    'zone': project['info']['datacenter_name'],
                    'checksum': project['checksum']
                }
        return checksum_portal_vdc

    dg_types: tuple = get_mongodb_objects('framework.types')

    def delete_all():
        for delete_dg_type in dg_types:
            # if delete_dg_type['public_id'] in list(range(171, 262)):
            # if delete_dg_type['description'] == 'passport-vm-%s' % portal_name:
            if 'passport-vm-' in delete_dg_type['description']:
                print(delete_dg_type['description'])
                # if 'pd20-' in delete_dg_type['label']:
                print('DELETE CMDB TYPE', cmdb_api('DELETE', "types/%s" % delete_dg_type['public_id'], cmdb_token))

        for categories in dg_categories:
            for categories_id in categories['results']:
                print('DELETE DG CAT', cmdb_api('DELETE', "categories/%s" % {categories_id['public_id']}, cmdb_token))

    # dg_types: tuple = get_all_jsons('types', cmdb_token)

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

    dg_vm_projects = list()

    for vm_type in dg_types:
        if vm_type['description'] == 'passport-vm-%s' % portal_name:
            if vm_type['name'] not in map(lambda x: x['id'], portal_projects['projects']):
                print('DELETE TYPE %s from CMDB' % vm_type['name'],
                      cmdb_api('DELETE', "types/%s" % vm_type['public_id'], cmdb_token))
            else:
                dg_vm_projects.append(vm_type)

    # vm_projects_ids = tuple(map(lambda x: x['name'], dg_vm_projects))

    from vdcPassports import PassportsVDC
    all_vdc_objects, dg_vdc_type = PassportsVDC(portal_name)

    project_id_vdc_types = dict()

    for project in portal_projects['projects']:
        # if project['id'] not in map(lambda x: x['name'] if x['description'] == 'passport-vm-%s' % portal_name else None,
        #                             dg_types):
        #     print('TYPE FOR DELETE', project['id'])

        # if project['id'] in ('803aa26d-5e77-42bd-8320-88056f09690e', '148d5303-579d-48f3-a54e-c8dea68b8e55'):
        #     print(project)
        # for vm_project in dg_vm_projects:
        for vdc_vm in all_vdc_objects:
            if vdc_vm['fields'][5]['value'] == project['id']:  # and vdc_vm['fields'][5]['value'] == vm_project['name']:
                project_id_vdc_types[project['id']] = {
                    'vdc_object_id': vdc_vm['public_id']
                }

                # {'vm_project_id': vm_project['public_id'],
            # if project['id'] not in dg_vm_projects_ids:
            # print(True, project['id'])
            # project_id_vdc_types[project['id']] = {'vdc_object_id': vdc_vm['public_id']}
        # {'vm_project_id': None,

    projects = checksum_vdc(portal_projects['projects'])

    del portal_projects

    # get_vdc_checksum = lambda foo: reduce(lambda x, y: x + y, map(lambda bar: tuple(
    #     map(lambda baz: dict(vdc_id=baz.get('name'), type_id=baz.get('public_id'),
    #                          check_sum=baz['render_meta']['sections'][0].get('label')), bar['results'])),
    #                                                               foo)) if foo else foo

    # dg_vdc_checksum = get_vdc_checksum(dg_types)

    # dg_vdc_checksum = tuple(map(lambda x: dict(vdc_id=x.get('name'), type_id=x.get('public_id'),
    #                                            check_sum=x['render_meta']['sections'][0].get('label')), dg_types))

    dg_vdc_checksum = map(lambda x: {
        'vdc_id': x['name'],
        'type_id': x['public_id'],
        'check_sum': x['render_meta']['sections'][0]['label']
    }, dg_types)

    update_dg_types = list()

    for project in projects:
        for dg_vdc in dg_vdc_checksum:
            if projects[project]['id'] == dg_vdc['vdc_id'] and projects[project]['checksum'] != dg_vdc['check_sum']:
                update_dg_types.append(dict(type_id=dg_vdc['type_id'], vdc_id=dg_vdc['vdc_id']))

    print('VDC WHERE WERE CHANGES', len(update_dg_types))

    portal_tags = portal_api('dict/tags', portal_name)['stdout']['tags']
    all_objects = get_mongodb_objects('framework.objects')

    for project in projects:
        if not any(map(lambda x: x['name'] == projects[project]['id'], dg_types)):
            vdc_id = project_id_vdc_types[projects[project]['id']]['vdc_object_id']

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
                            "name": projects[project]['id'],
                            "label": projects[project]['checksum']
                        }
                    ],
                    # "externals": [],
                    "externals": [
                        {
                            "name": "vdc link",
                            "href": "%s/client/orders/%s" % (portal_info[portal_name]['url'], projects[project]['id']),
                            "label": "Vdc link",
                            "icon": "fas fa-external-link-alt",
                            "fields": []
                        },
                        {
                            "name": "vm link",
                            "href": "%s/client/orders/%s/servers/{}/info" % (portal_info[portal_name]['url'],
                                                                             projects[project]['id']),
                            "label": "Vm link",
                            "icon": "fas fa-external-link-alt",
                            "fields": ["vm-id"]
                        }
                    ],
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
                "name": projects[project]['id'],
                "label": f"{project} | {projects[project]['zone']} | {projects[project]['id']}",
                "description": f'passport-vm-%s' % portal_name
            }

            create_type = cmdb_api('POST', 'types/', cmdb_token, payload_type_tmp)
            print(create_type, 'create_type')
            print(create_type['result_id'], 'new type id')

            dg_categories: tuple = get_mongodb_objects('framework.categories')

            category_search: dict = \
                max(filter(lambda y: y['name'] == "group_id--%s" % projects[project]['group_id'], dg_categories))

            payload_category_tmp: dict = {
                "public_id": category_search['public_id'],
                "name": category_search['name'],
                "label": category_search['label'],
                "meta": {
                    "icon": "fas fa-folder-open",
                    "order": None
                },
                "parent": category_search['parent'],
                "types": category_search['types']
            }

            payload_category_tmp['types'].append(create_type['result_id'])

            cmdb_api('PUT', "categories/%s" % category_search['public_id'], cmdb_token, payload_category_tmp)

            print('payload_category_tmp', payload_category_tmp)

            vm_list: dict = portal_api(f"servers?project_id={projects[project]['id']}", portal_name)

            for server in vm_list['stdout']['servers']:
                time.sleep(0.1)
                try:
                    create_object = objects(server, cmdb_token, create_type['result_id'], user_id, tags=portal_tags,
                                            vdc_object=vdc_id)
                    print('CREATE OBJECT IN %s' % create_type['result_id'], create_object)
                except:
                    time.sleep(5)
                    objects(server, cmdb_token, create_type['result_id'], user_id, tags=portal_tags, vdc_object=vdc_id)

    if not update_dg_types:
        return all_objects

    for dg_type in update_dg_types:

        vdc_id = project_id_vdc_types[dg_type['vdc_id']]['vdc_object_id']

        vm_list = portal_api(f"servers?project_id={dg_type['vdc_id']}", portal_name)

        dg_type_objects = tuple(filter(lambda x: x['type_id'] == dg_type['type_id'], all_objects))

        portal_project_vms = \
            tuple(map(lambda server: objects(server, 'token', dg_type['type_id'], user_id, 'GET_TEMPLATE',
                                             tags=portal_tags, vdc_object=vdc_id).get('fields'),
                      vm_list['stdout']['servers']))

        for portal_vm in portal_project_vms:
            if not any(map(lambda x: x['fields'][17]['value'] == portal_vm[17]['value'], dg_type_objects)):
                print('VM FOR CREATE', portal_vm)
                objects(portal_vm, cmdb_token, dg_type['type_id'], user_id, 'POST_NEW_VM', tags=portal_tags,
                        vdc_object=vdc_id)

            for dg_object in dg_type_objects:
                if dg_object['fields'][17]['value'] == portal_vm[17]['value'] and dg_object['fields'] != portal_vm:
                    print("VM FOR UPDATE IN %s" % dg_type['type_id'], portal_vm)

                    payload_object_tmp: dict = {
                        "type_id": dg_type['type_id'],
                        "status": dg_object['status'],
                        "version": dg_object['version'],
                        "creation_time": {
                            "$date": int(time.mktime(dg_object['creation_time'].timetuple()) * 1000)
                        },
                        "author_id": dg_object['author_id'],
                        "last_edit_time": {
                            "$date": int(time.time() * 1000)
                        },
                        "editor_id": user_id,
                        "active": dg_object['active'],
                        "fields": portal_vm,
                        "public_id": dg_object['public_id'],
                        "views": dg_object['views'],
                        "comment": ""
                    }

                    time.sleep(0.1)
                    print(objects(payload_object_tmp, cmdb_token, dg_type['type_id'], user_id, 'PUT',
                                  tags=portal_tags, vdc_object=vdc_id))

        for object in filter(lambda x: x[1][17]['value'] not in map(lambda x: x[17]['value'], portal_project_vms),
                             map(lambda y: (y.get('public_id'), y.get('fields')), dg_type_objects)):
            print('Delete object', object)
            cmdb_api('DELETE', "object/%s" % object[0], cmdb_token)

        get_info_dg_vdc = max(filter(lambda y: y['name'] == dg_type['vdc_id'], dg_types))

        get_info_dg_vdc['id'] = get_info_dg_vdc['name']

        get_info_dg_vdc = get_vdc_checksum(get_info_dg_vdc)

        del get_info_dg_vdc['info']['id'], get_info_dg_vdc['info']['_id']
        get_info_dg_vdc['info']['render_meta']['sections'][0]['label'] = get_info_dg_vdc['checksum']
        get_info_dg_vdc['info']['last_edit_time'] = \
            time.strftime(f'%Y-%m-%dT%H:%M:%S.{str(time.time())[-5:]}0', time.localtime(time.time()))
        get_info_dg_vdc['info']['creation_time'] = json_serial(get_info_dg_vdc['info']['creation_time'])

        print('##' * 20, 'UPDATE CHECKSUM', '##' * 20)

        print(dg_type['type_id'])
        print(get_info_dg_vdc['info'])

        print(cmdb_api('PUT', 'types/%s' % dg_type["type_id"], cmdb_token, get_info_dg_vdc['info']))

    return all_objects
