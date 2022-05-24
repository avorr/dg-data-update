#!/usr/local/bin/python3

import time
import datetime
from loguru import logger
from collections import defaultdict

from common_function import cmdb_api
from common_function import category_id
from common_function import get_mongodb_objects


def PassportsVDC(portal_name: str, dg_token: str, user_id: str, portal_projects: list,
                 all_objects: tuple = ()) -> tuple | None:
    all_categories: tuple = get_mongodb_objects('framework.categories')

    vdc_category_id: dict = \
        category_id('passports-vdc', 'Passports VDC', 'fas fa-network-wired', dg_token, all_categories)

    def create_vdc(vdc_info: dict, dg_token: str, type_id: str, author_id: int, method: str = 'POST',
                   template: bool = False) -> dict | str:
        if method == 'PUT':
            return cmdb_api(method, 'object/%s' % type_id, dg_token, vdc_info)

        def networks_info(networks: list, dns_servers: bool, subnet: bool) -> str | tuple[str, str, str, str]:
            networks = tuple(map(lambda x: defaultdict(str, x), networks))
            if dns_servers:
                dns_info = list()
                for network in networks:
                    dns_info.append(network["dns_nameservers"])
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

        subnet_name, subnet_uuid, network_name, network_uuid = networks_info(vdc_info["networks"], False, True)

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

        return cmdb_api("POST", "object/", dg_token, payload_vcd_object)

    dg_types: tuple = get_mongodb_objects("framework.types")

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
                        "name": "VDC-%s" % portal_name,
                        "label": "VDC-%s" % portal_name
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
            "name": "VDC-%s" % portal_name,
            "label": "VDC-%s" % portal_name,
            "description": "VDC-%s" % portal_name
        }

        create_type: dict = cmdb_api("POST", "types/", dg_token, payload_type_tmp)
        logger.info(f"Create new type with id -> {create_type['result_id']}")

        payload_category: dict = {
            "public_id": vdc_category_id["public_id"],
            "name": vdc_category_id["name"],
            "label": vdc_category_id["label"],
            "meta": {
                # "icon": "far fa-folder-open",
                "icon": "fas fa-network-wired",
                "order": None
            },
            "parent": None,
            "types": vdc_category_id["types"]
        }

        if not create_type['result_id']:
            return

        payload_category['types'].append(create_type['result_id'])

        put_type_in_cat = cmdb_api('PUT', "categories/%s" % vdc_category_id['public_id'], dg_token, payload_category)
        logger.info(f"Put type {put_type_in_cat} in category {payload_category['name']}")

        for vdc in portal_projects:
            create_vdc_object = create_vdc(vdc, dg_token, create_type['result_id'], user_id)
            print(create_vdc_object)
            time.sleep(0.1)

    if "create_type" in locals():
        dg_vdc_type: dict = {
            "public_id": locals()["create_type"]["result_id"]
        }
        logger.info("There is type id in locals variables")
    else:
        dg_vdc_type: dict = max(filter(lambda x: x['name'] == "VDC-%s" % portal_name, dg_types))
    del dg_types

    all_objects: tuple = get_mongodb_objects("framework.objects")
    all_vdc_objects = tuple(filter(lambda x: x["type_id"] == dg_vdc_type["public_id"], all_objects))

    del all_objects

    for dg_object in all_vdc_objects:
        if dg_object["fields"][5]["value"] not in tuple(map(lambda x: x["id"], portal_projects)):
            type_for_delete: tuple = get_mongodb_objects("framework.types", {"name": dg_object["fields"][5]["value"]})
            if type_for_delete:
                cmdb_api("DELETE", "types/%s" % max(type_for_delete)["public_id"], dg_token)
                logger.info(f'Delete vdc object {dg_object["fields"][0]["value"]} from type {dg_vdc_type["public_id"]}')
            cmdb_api('DELETE', "object/%s" % dg_object['public_id'], dg_token)
            logger.info(f'Delete vdc object {dg_object["fields"][0]["value"]} from type {dg_vdc_type["public_id"]}')

    for vdc in portal_projects:
        for dg_object in all_vdc_objects:

            vdc_template: dict | str = create_vdc(vdc, dg_token, dg_vdc_type['public_id'], user_id, template=True)
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

                create_vdc(payload_object_tmp, dg_token, dg_object['public_id'], user_id, 'PUT')
                logger.info(f'Update object {dg_object["public_id"]} IN TYPE {dg_object["type_id"]}')

        if vdc["id"] not in map(lambda x: x['fields'][5]['value'], all_vdc_objects):
            # all_vdc_objects.append({})
            create_vdc(vdc, dg_token, dg_vdc_type["public_id"], user_id)
            logger.info(f'Create vdc {vdc["name"]} in type {dg_vdc_type["public_id"]}')

    all_objects: tuple = get_mongodb_objects('framework.objects')
    all_vdc_objects = tuple(filter(lambda x: x['type_id'] == dg_vdc_type['public_id'], all_objects))

    return all_vdc_objects, dg_vdc_type
