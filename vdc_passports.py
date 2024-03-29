#!/usr/local/bin/python3

import time
from loguru import logger
from collections import defaultdict
from datetime import datetime

from env import portal_info
from common_function import dg_api, category_id, get_mongodb_objects


def passports_vdc(region: str, auth_info: tuple, domains, projects: list, all_objects: tuple = ()) -> tuple | None:
    """
    Func to create vdc objects in DG
    :param region:
    :param auth_info:
    :param domains:
    :param projects:
    :param all_objects:
    :return: tuple
    """

    dg_token, user_id = auth_info

    all_categories: tuple = get_mongodb_objects('framework.categories')

    vdc_category_id: dict = category_id("passports-vdc", 'Passports Vdc', 'fas fa-network-wired', dg_token,
                                        all_categories)

    def create_vdc(vdc_info: dict, type_id: int, method: str = 'POST', template: bool = False) -> dict | str:
        if method == "PUT":
            return dg_api(method, "object/%s" % type_id, dg_token, vdc_info)

        def networks_info(networks: list, dns_servers: bool, subnet: bool) -> str | tuple[str, str, str, str]:
            networks = tuple(map(lambda x: defaultdict(str, x), networks))
            if dns_servers:
                dns_info = list()
                for network in networks:
                    dns_info.append(network["dns_nameservers"])
                return ' | '.join(map(lambda x: ', '.join(x), dns_info))

            cidrs = list()

            if subnet:
                subnet_names, subnet_uuids, network_names, network_uuids = list(), list(), list(), list()
                for network in networks:
                    subnet_names.append(network["subnet_name"])
                    subnet_uuids.append(network["subnet_uuid"])
                    network_names.append(network["network_name"])
                    network_uuids.append(network["network_uuid"])
                return ' | '.join(subnet_names), ' | '.join(subnet_uuids), \
                    ' | '.join(network_names), ' | '.join(network_uuids)

            for network in networks:
                cidrs.append(f'{network["cidr"]}({network["network_name"]})')
            return ' | '.join(cidrs)

        subnet_name, subnet_uuid, network_name, network_uuid = networks_info(vdc_info["networks"], False, True)

        payload_vdc_object: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": user_id,
            "fields": [
                {
                    "name": "name",
                    "value": vdc_info["name"]
                },
                {
                    "name": "desc",
                    "value": vdc_info["desc"]
                    # "value": vdc_info["desc"] if "desc" in vdc_info else ""
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
                    "name": "domain",
                    "value": domains[vdc_info["domain_id"]]
                },
                {
                    "name": "group",
                    "value": vdc_info["group_name"]
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
                },
                {
                    "name": "record-update-time",
                    "value": datetime.now().strftime('%d.%m.%Y %H:%M')
                }
            ]
        }

        if template:
            return payload_vdc_object

        return dg_api("POST", "object/", dg_token, payload_vdc_object)

    dg_types: tuple = get_mongodb_objects("framework.types")

    if not any(filter(lambda x: x['name'] == "vdc-%s" % region, dg_types)):

        payload_type_tmp: dict = {
            "fields": [
                {
                    "type": "text",
                    "name": "name",
                    "label": "name"
                },
                {
                    "type": "text",
                    "name": "desc",
                    "label": "desc"
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
                    "name": "domain",
                    "label": "domain"
                },
                {
                    "type": "text",
                    "name": "group",
                    "label": "group"
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
                },
                {
                    "type": "text",
                    "name": "record-update-time",
                    "label": "record update time"
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
                            "desc",
                            "datacenter-name",
                            "networks",
                            "dns-nameservers",
                            "openstack-id",
                            "project-id",
                            "default-network",
                            "domain",
                            "group",
                            "subnet-name",
                            "subnet-uuid",
                            "network-name",
                            "network-uuid",
                            "record-update-time"
                        ],
                        "type": "section",
                        "name": "vdc-%s" % region,
                        "label": "VDC-%s" % region.upper()
                    }
                ],
                "externals": [
                    {
                        "name": "vdc link",
                        "href": "%s/client/orders/{}" % portal_info['url'],
                        "label": "Vdc link",
                        "icon": "fas fa-external-link-alt",
                        "fields": [
                            "project-id"
                        ]
                    }
                ],
                "summary": {
                    "fields": [
                        "name",
                        "desc",
                        "datacenter-name",
                        # "networks",
                        "domain",
                        "group",
                        # "dns-nameservers",
                        # "record-update-time"
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
            "name": "vdc-%s" % region,
            "label": "VDC-%s" % region.upper(),
            "description": "VDC-%s" % region.upper()
        }

        create_type: dict = dg_api("POST", "types/", dg_token, payload_type_tmp)
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

        put_type_in_cat = dg_api('PUT', "categories/%s" % vdc_category_id['public_id'], dg_token, payload_category)
        logger.info(f"Put type {put_type_in_cat['result']['public_id']} in category {payload_category['name']}")

        for vdc in projects:
            create_vdc_object = create_vdc(vdc, create_type['result_id'])
            logger.info(f"Create vdc object {create_vdc_object} in {create_type['result_id']}")

    if "create_type" in locals():
        dg_vdc_type: dict = {
            "public_id": locals()["create_type"]["result_id"]
        }
        logger.info("There is type id in locals variables")
    else:
        dg_vdc_type: dict = max(filter(lambda x: x['name'] == "vdc-%s" % region, dg_types))
    del dg_types

    if not all_objects:
        all_objects: tuple = get_mongodb_objects("framework.objects")
    all_vdc_objects = tuple(filter(lambda x: x["type_id"] == dg_vdc_type["public_id"], all_objects))

    del all_objects

    for dg_object in all_vdc_objects:
        if dg_object["fields"][8]["value"] not in tuple(map(lambda x: x["id"], projects)):
            type_for_delete: tuple = get_mongodb_objects("framework.types", {"name": dg_object["fields"][8]["value"]})
            if type_for_delete:
                dg_api("DELETE", "types/%s" % max(type_for_delete)["public_id"], dg_token)
                logger.info(f'Delete vdc object {dg_object["fields"][0]["value"]} from type {dg_vdc_type["public_id"]}')
            dg_api('DELETE', "object/%s" % dg_object['public_id'], dg_token)
            logger.info(f'Delete vdc object {dg_object["fields"][0]["value"]} from type {dg_vdc_type["public_id"]}')

    for vdc in projects:
        for dg_object in all_vdc_objects:

            vdc_template: dict | str = create_vdc(vdc, dg_vdc_type['public_id'], template=True)

            dg_to_diff = dg_object["fields"].copy()
            tmp_to_diff = vdc_template["fields"].copy()
            dg_to_diff.pop(-1)
            tmp_to_diff.pop(-1)

            # if vdc["id"] == dg_object["fields"][8]['value'] and dg_object["fields"] != vdc_template["fields"]:
            if vdc["id"] == dg_object["fields"][8]['value'] and dg_to_diff != tmp_to_diff:
                payload_object_tmp: dict = {
                    "type_id": dg_object['type_id'],
                    "status": dg_object['status'],
                    "version": dg_object['version'],
                    "creation_time": {
                        "$date": int(datetime.timestamp(dg_object['creation_time']) * 1000)
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

                create_vdc(payload_object_tmp, dg_object['public_id'], 'PUT')
                logger.info(f'Update object {dg_object["public_id"]} in type {dg_object["type_id"]}')

        if vdc["id"] not in tuple(map(lambda x: x['fields'][8]['value'], all_vdc_objects)):
            create_vdc(vdc, dg_vdc_type["public_id"])
            logger.info(f'Create vdc {vdc["name"]} in type {dg_vdc_type["public_id"]}')

    all_objects: tuple = get_mongodb_objects('framework.objects')
    all_vdc_objects = tuple(filter(lambda x: x['type_id'] == dg_vdc_type['public_id'], all_objects))

    return all_vdc_objects, dg_vdc_type
