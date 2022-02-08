#!/usr/bin/python3

import time
from typing import Union, Tuple

import requests
import datetime
from pymongo import MongoClient
from collections import defaultdict
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from tools import *
from env import portal_info
from vm_passport import get_mongodb_objects
from vm_passport import portal_api
from vm_passport import cmdb_api
from vm_passport import categorie_id
from vm_passport import getCmdbToken
from vm_passport import getInfoFromAllPage

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def PassportsVDC(portal_name: str, all_objects: tuple = ()) -> tuple:
    cmdb_token, user_id = getCmdbToken()
    allCategories = getInfoFromAllPage('categories', cmdb_token)

    vdc_categorie_id = \
        categorie_id('passports-vdc', 'Passports VDC', 'fas fa-network-wired', cmdb_token, allCategories)

    # osPortalCategorieId = categorie_id(f'VDC-{portal_name}', f'VDC-{portal_name}', 'fas fa-folder-open',
    #                                    cmdb_token, allCategories, vdc_categorie_id['public_id'])

    def create_vdc(vdc_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
                   template: bool = False) -> dict:
        if method == 'PUT':
            return cmdb_api(method, 'object/%s' % type_id, cmdb_token, vdc_info)

        def networks_info(networks: list, dns_servers: bool,
                          subnet: bool) -> str:  # Union[str, tuple[str, str, str, str]]:
            networks = tuple(map(lambda x: defaultdict(str, x), networks))
            if dns_servers:
                dns_info = list()
                for network in networks:
                    dns_info.append(network['dns_nameservers'])
                return '\n#'.join(map(lambda x: ', '.join(x), dns_info))
            cidrs = list()
            if subnet:
                subnet_names, subnet_uuids, network_names, network_uuids = list(), list(), list(), list()
                for network in networks:
                    subnet_names.append(network['subnet_name'])
                    subnet_uuids.append(network['subnet_uuid'])
                    network_names.append(network['network_name'])
                    network_uuids.append(network['network_uuid'])
                return '\n'.join(subnet_names), '\n'.join(subnet_uuids), \
                       '\n'.join(network_names), '\n'.join(network_uuids)

            for network in networks:
                cidrs.append(network['cidr'])
            return '\n'.join(cidrs)

        subnet_name, subnet_uuid, network_name, network_uuid = networks_info(vdc_info['networks'], False, True)

        payload_vcd_object: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "name",
                    "value": vdc_info["name"]
                },
                {
                    "name": "datacenter-name",
                    "value": vdc_info["datacenter_name"]
                },
                {
                    "name": "networks",
                    "value": networks_info(vdc_info["networks"], dns_servers=False, subnet=False)
                },
                {
                    "name": "dns-nameservers",
                    "value": networks_info(vdc_info["networks"], dns_servers=True, subnet=False)
                },
                {
                    "name": "openstack-id",
                    "value": vdc_info["openstack_project_id"]
                },
                {
                    "name": "project-id",
                    "value": vdc_info["id"]
                },
                {
                    "name": "default-network",
                    "value": vdc_info["default_network"]
                },
                {
                    "name": "subnet-name",
                    "value": subnet_name
                },
                {
                    "name": "subnet-uuid",
                    "value": subnet_uuid
                },
                {
                    "name": "network-name",
                    "value": network_name
                },
                {
                    "name": "network-uuid",
                    "value": network_uuid
                }
            ]
        }

        if template:
            return payload_vcd_object

        return cmdb_api("POST", "object/", cmdb_token, payload_vcd_object)
        # json_read(payload_vcd_object)


    # dg_types: tuple = getInfoFromAllPage('types', cmdb_token)
    from vm_passport import get_mongodb_objects
    dg_types: tuple = get_mongodb_objects('framework.types')

    portal_vdces: list = portal_api("projects", portal_name)["stdout"]["projects"]

    if not any(filter(lambda x: x['name'] == "VDC-%s" % portal_name, dg_types)):

        payload_type_tmp: dict = {
            "fields": [
                {
                    "type": "text",
                    "name": "name",
                    "label": "name"
                },
                {
                    "type": "text",
                    "name": "datacenter-name",
                    "label": "datacenter name"
                },
                {
                    "type": "text",
                    "name": "networks",
                    "label": "networks"
                },
                {
                    "type": "text",
                    "name": "dns-nameservers",
                    "label": "dns nameservers"
                },
                {
                    "type": "text",
                    "name": "openstack-id",
                    "label": "openstack id"
                },
                {
                    "type": "text",
                    "name": "project-id",
                    "label": "project id"
                },
                {
                    "type": "text",
                    "name": "default-network",
                    "label": "default network"
                },
                {
                    "type": "text",
                    "name": "subnet-name",
                    "label": "subnet name"
                },
                {
                    "type": "text",
                    "name": "subnet-uuid",
                    "label": "subnet uuid"
                },
                {
                    "type": "text",
                    "name": "network-name",
                    "label": "network name"
                },
                {
                    "type": "text",
                    "name": "network-uuid",
                    "label": "network uuid"
                }
            ],
            "active": True,
            "version": "1.0.0",
            "author_id": user_id,
            "render_meta": {
                "icon": "fab fa-battle-net",
                "sections": [
                    {
                        "fields": [
                            "name",
                            "datacenter-name",
                            "networks",
                            "dns-nameservers",
                            "openstack-id",
                            "project-id",
                            "default-network",
                            "subnet-name",
                            "subnet-uuid",
                            "network-name",
                            "network-uuid"
                        ],
                        "type": "section",
                        "name": f"VDC-{portal_name}",
                        "label": f"VDC-{portal_name}"
                    }
                ],
                "externals": [],
                "summary": {
                    "fields": [
                        "name",
                        "datacenter-name",
                        "networks",
                        "dns-nameservers"
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
            "name": f"VDC-{portal_name}",
            "label": f"VDC-{portal_name}",
            "description": f"VDC-{portal_name}"
        }

        create_type = cmdb_api("POST", "types/", cmdb_token, payload_type_tmp)
        print(create_type)
        all_types_pages = getInfoFromAllPage("types", cmdb_token)[0]["pager"]["total_pages"]

        new_all_types_pages = list()
        for page in range(1, all_types_pages + 1):
            responsePage = cmdb_api("GET", f"types/?page={page}", cmdb_token)
            new_all_types_pages.append(responsePage)

        new_type_id = None
        for new_type in new_all_types_pages:
            for newItem in new_type['results']:
                if newItem['name'] == f"VDC-{portal_name}":
                    new_type_id = newItem['public_id']

        print(new_type_id, 'new type id')
        payload_categorie: dict = {
            "public_id": vdc_categorie_id["public_id"],
            "name": vdc_categorie_id["name"],
            "label": vdc_categorie_id["label"],
            "meta": {
                # "icon": "far fa-folder-open",
                "icon": "fas fa-network-wired",
                "order": None
            },
            "parent": None,
            "types": vdc_categorie_id["types"]
        }

        if new_type_id == None:
            return

        payload_categorie['types'].append(new_type_id)

        put_type_in_cat = cmdb_api('PUT', f"categories/{vdc_categorie_id['public_id']}", cmdb_token, payload_categorie)
        print('put_type_in_cat', put_type_in_cat)
        print('payload_categorie', payload_categorie)

        for vdc in portal_vdces:
            create_vdc_object = create_vdc(vdc, cmdb_token, new_type_id, user_id)
            print(create_vdc_object)
            time.sleep(0.1)

    if 'new_type_id' in locals():
        dg_vdc_type: dict = {'public_id': locals()['new_type_id']}
        print('new_type_id in locals')
    else:
        dg_vdc_type: dict = max(filter(lambda x: x['name'] == "VDC-%s" % portal_name, dg_types))

    del dg_types

    #from allObjects import all_objects
    from vm_passport import get_mongodb_objects
    # all_objects = get_mongodb_objects('framework.objects')

    all_objects = get_mongodb_objects('framework.objects')
    all_vdc_objects = tuple(filter(lambda x: x['type_id'] == dg_vdc_type['public_id'], all_objects))

    # print(all_vdc_objects)
    # return
    # for i in all_vdc_objects:
    #     print(i)
    # print(all_vdc_objects[0])
    # print('******')
    # print(portal_vdces[0])
    # return

    del all_objects

    for dg_object in all_vdc_objects:
        if dg_object['fields'][5]['value'] not in map(lambda x: x['id'], portal_vdces):
            print(f"DELETE OBJECT {dg_object['fields'][0]['value']} FROM TYPE {dg_vdc_type['public_id']}")
            cmdb_api('DELETE', "object/%s" % dg_object['public_id'], cmdb_token)

    for vdc in portal_vdces:
        for dg_object in all_vdc_objects:

            vdc_template = create_vdc(vdc, cmdb_token, dg_vdc_type['public_id'], user_id, template=True)
            if vdc["id"] == dg_object["fields"][5]['value'] and dg_object["fields"] != vdc_template["fields"]:
                payload_object_tmp: dict = {
                    "type_id": dg_object['type_id'],
                    "status": dg_object['status'],
                    "version": dg_object['version'],
                    "creation_time": {
                        "$date": int(datetime.datetime.timestamp(dg_object['creation_time']) * 1000)
                    },
                    "author_id": dg_object['author_id'],
                    "last_edit_time": {
                        "$date": int(time.time() * 1000)
                    },
                    "editor_id": user_id,
                    "active": dg_object['active'],
                    "fields": vdc_template['fields'],
                    "public_id": dg_object['public_id'],
                    "views": dg_object['views'],
                    "comment": ""
                }

                create_vdc(payload_object_tmp, cmdb_token, dg_object['public_id'], user_id, 'PUT')
                print(f'UPDATE OBJECT {dg_object["public_id"]} IN TYPE {dg_object["type_id"]}')

        if vdc["id"] not in map(lambda x: x['fields'][5]['value'], all_vdc_objects):
            # all_vdc_objects.append({})
            create_vdc(vdc, cmdb_token, dg_vdc_type["public_id"], user_id)
            print(f'CREATE VDC {vdc["name"]} IN TYPE {dg_vdc_type["public_id"]}')

    from vm_passport import get_mongodb_objects
    all_objects = get_mongodb_objects('framework.objects')
    all_vdc_objects = tuple(filter(lambda x: x['type_id'] == dg_vdc_type['public_id'], all_objects))

    return all_vdc_objects, dg_vdc_type


if __name__ == '__main__':
    PassportsVDC('PD15')
