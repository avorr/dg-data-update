#!/usr/local/bin/python3

import time
import hashlib
import json
from loguru import logger
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from env import portal_info
from vdc_passports import passports_vdc
from common_function import dg_api, \
    get_mongodb_objects, \
    create_category, \
    category_id, \
    json_serial, \
    portal_api


def passports_vm(region: str, auth_info: tuple) -> tuple | None:
    """
    Main func for create vm objects in DataGerry
    :param region: ex: PD15
    :param auth_info: ex: PD15
    :return: tuple
    """

    dg_token, user_id = auth_info

    portal_tags: list = portal_api("dict/tags")["stdout"]["tags"]

    def vm_objects(vm_info: dict, type_id: int, project_networks: list, method: str = "POST", template: bool = False,
                   vdc_object=None) -> dict:
        """
        Func to create or update or delete objects in DataGerry
        :param vm_info:
        :param type_id:
        :param project_networks:
        :param method:
        :param template:
        :param vdc_object:
        :return:
        """
        if method == "PUT":
            return dg_api(method, "object/%s" % vm_info["public_id"], dg_token, vm_info)

        elif method == "POST_VM":

            payload_vm: dict = {
                "status": True,
                "type_id": type_id,
                "version": "1.0.0",
                "author_id": user_id,
                "fields": vm_info
            }

            return dg_api("POST", "object/", dg_token, payload_vm)

        extra_disks: str = ""
        if vm_info["volumes"]:
            def all_disks(x: dict, y: int) -> str:
                return f'{extra_disks}{x[y]["size"]} '

            for ex_disk in range(len(vm_info["volumes"])):
                extra_disks = all_disks(vm_info["volumes"], ex_disk)

        def sum_disks(x: str) -> int:
            return sum(map(int, x.rstrip().split(" "))) if x else x

        def check_public_ip(x: str, y: dict) -> str:
            return y[x]["address"] if x in y else ""

        if "security_groups" in vm_info:
            for rule in vm_info["security_groups"]:
                all_ports = tuple(
                    filter(lambda x, y="protocol": x[y] and x[y] != "icmp" if x[y] else x[y], rule["rules"]))
                ingress_ports = tuple(
                    filter(lambda x: x["direction"] == "ingress" if "direction" in x else "", all_ports))
                ingress_ports = tuple(map(lambda x: defaultdict(str, x), ingress_ports))
                egress_ports = tuple(
                    filter(lambda x: x["direction"] == "egress" if "direction" in x else "", all_ports))
                egress_ports = tuple(map(lambda x: defaultdict(str, x), egress_ports))
        else:
            ingress_ports = egress_ports = ""

        def conversion_ports_to_string(x: dict, foo="port_range_max", bar="port_range_min") -> str:
            return f"{x['protocol']} {x[foo]}" if x[foo] == x[bar] else f"{x['protocol']} {x[bar]}-{x[foo]}"

        def get_tag_name(vm_info: list) -> str:
            """
            Func to get tag from server json
            :param vm_info:
            :return:
            """
            if vm_info["tag_ids"]:
                vm_tag_names = list()
                for vm_tag in vm_info["tag_ids"]:
                    for tag in portal_tags:
                        if tag["id"] == vm_tag:
                            vm_tag_names.append(tag["tag_name"])
                if len(vm_tag_names) == 1:
                    return vm_tag_names[0]
                return " \n".join(vm_tag_names)
            else:
                return ""

        def check_creation_date(x: str) -> str:
            return x[:10] if x else ""

        def network_name(networks: list, network_uuid: str) -> str:
            for net in networks:
                if 'network_uuid' in net:
                    if net['network_uuid'] == network_uuid:
                        return net["network_name"]
            return "network without uuid"

        payload_vm: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": user_id,
            "fields": [
                {
                    "name": "name",
                    "value": vm_info['service_name']
                },
                {
                    "name": "vm-name",
                    "value": vm_info["name"]
                },
                {
                    "name": "os-type",
                    "value": f"{vm_info['os_name']} {str(vm_info['os_version'])}"
                },
                {
                    "name": "flavor",
                    "value": vm_info["flavor"]
                },
                {
                    "name": "cpu",
                    "value": vm_info["cpu"]
                },
                {
                    "name": "ram",
                    "value": vm_info["ram"]
                },
                {
                    "name": "disk",
                    "value": vm_info["disk"]
                },
                {
                    "name": "additional-disk",
                    "value": sum_disks(extra_disks)
                },
                {
                    "name": "network-name",
                    "value": network_name(project_networks, vm_info["network_uuid"])
                },
                {
                    "name": "summary-vm-info",
                    "value": f"{vm_info['cpu']}/{vm_info['ram']}/{vm_info['disk']} \n{'/'.join(extra_disks.rstrip().split())}"
                },
                {
                    "name": "local-ip",
                    "value": vm_info["ip"]
                },
                {
                    "name": "public-ip",
                    "value": check_public_ip("public_ip", vm_info)
                },
                {
                    "name": "tags",
                    "value": get_tag_name(vm_info)
                },
                {
                    "name": "description",
                    "value": vm_info["comment"] if "comment" in vm_info else ""
                },
                {
                    "name": "zone",
                    "value": vm_info["region_name"]
                },
                {
                    "name": "ingress-ports",
                    "value": " \n".join(tuple(map(conversion_ports_to_string, ingress_ports)))
                },
                {
                    "name": "egress-ports",
                    "value": " \n".join(tuple(map(conversion_ports_to_string, egress_ports)))
                },
                {
                    "name": "state",
                    "value": vm_info["state"]
                },
                {
                    "name": "creator",
                    "value": vm_info["creator_login"]
                },
                {
                    "name": "vm-id",
                    "value": vm_info["id"]
                },
                {
                    "name": "os-id",
                    "value": vm_info["openstack_server_id"]
                },
                {
                    "name": "creation-date",
                    "value": check_creation_date(vm_info["order_created_at"])
                },
                {
                    "name": "record-update-time",
                    "value": datetime.now().strftime('%d.%m.%Y %H:%M')
                },
                {
                    "name": "vdc-link",
                    "value": vdc_object
                }
            ]
        }
        if template:
            return payload_vm

        return dg_api(method, "object/", dg_token, payload_vm)

    dg_categories: tuple = get_mongodb_objects("framework.categories")

    vm_category_id: dict = category_id("passports", "Passports Vm", "far fa-folder-open", dg_token, dg_categories)

    portal_category_id: dict = category_id(region, region.upper(), "fas fa-folder-open", dg_token, dg_categories,
                                           vm_category_id["public_id"])

    domains: list = portal_api("domains")["stdout"]["domains"]

    domains: dict = {
        domain["id"]: domain["name"] for domain in domains
    }
    for domain_id in domains:
        if not any(map(lambda y: y["name"] == "domain_id--%s" % domain_id, dg_categories)):
            create_category("domain_id--%s" % domain_id, domains[domain_id], "far fa-folder-open", dg_token,
                            portal_category_id["public_id"])

    portal_groups_info: list = portal_api("groups?per_page=1000")["stdout"]["groups"]

    dg_categories: tuple = get_mongodb_objects("framework.categories")

    for group_id in portal_groups_info:
        if not any(map(lambda y: y["name"] == "group_id--%s" % group_id["id"], dg_categories)):
            for domain in dg_categories:
                if domain["name"] == "domain_id--%s" % group_id["domain_id"]:
                    create_category("group_id--%s" % group_id["id"], group_id["name"],
                                    "fas fa-folder-open", dg_token, domain["public_id"])

    # print(tuple(map(lambda y: f'group_id--{y["id"]}', portal_groups_info)))
    # print(portal_category_id)
    # for dg_category in dg_categories:
    #     if dg_category["name"][:10] == "group_id--" and dg_category['parent'] == portal_category_id['public_id']:
    # if dg_category["name"] not in tuple(map(lambda y: f'group_id--{y["id"]}', portal_groups_info)):
    # print(dg_category)

    # for portal_group in portal_groups_info:
    #     print(f'group_id--{portal_group["id"]}')

    portal_projects: list = portal_api("projects")["stdout"]["projects"]

    # for i in portal_projects:
    #     if i["name"] == 'gt-common-dmz':
    #         portal_projects = [i]

    def get_vdc_checksum(vdc_info: dict) -> dict:
        """
        Func to get vdc checksum from portal
        :param vdc_info:
        :return:
        """
        # vdc_checksum = portal_api(f"projects/{vdc_info["id"]}/checksum")
        vdc_checksum: dict = portal_api("servers?project_id=%s" % vdc_info["id"])
        return {
            "info": vdc_info,
            "checksum": hashlib.md5(json.dumps(vdc_checksum["stdout"]).encode()).hexdigest()
        }

    def checksum_vdc(cloud_projects: list) -> dict:
        """
        Func to get vdc checksum from portal
        :param cloud_projects:
        :return: dict
        """
        checksum_portal_vdc = dict()
        # with ThreadPoolExecutor(max_workers=thread_count(len(cloud_projects))) as executor:
        with ThreadPoolExecutor(max_workers=4) as executor:
            for project in executor.map(get_vdc_checksum, cloud_projects):
                checksum_portal_vdc[project["info"]["id"]] = {
                    "name": project["info"]["name"],
                    "domain_id": project["info"]["domain_id"],
                    "group_id": project["info"]["group_id"],
                    "zone": project["info"]["datacenter_name"],
                    "checksum": project["checksum"],
                    "networks": project["info"]["networks"],
                }
        return checksum_portal_vdc

    dg_types: tuple = get_mongodb_objects("framework.types")

    dg_vm_projects = list()

    for vm_type in dg_types:
        # if vm_type["description"] == f"passport-vm-{region}" or
        # f"{region}.foms.gtp" in vm_type["description"]:
        if vm_type["render_meta"]["sections"][0]["name"] == f"passport-vm-{region}":
            if vm_type['name'] not in tuple(map(lambda x: x["id"], portal_projects)):
                dg_api("DELETE", "types/%s" % vm_type["public_id"], dg_token)
                logger.info("Delete type %s from dg" % vm_type["name"])
            else:
                dg_vm_projects.append(vm_type)

    vdc_objects, dg_vdc_type = passports_vdc(region, auth_info, domains, portal_projects)

    project_id_vdc_types = dict()

    for project in portal_projects:
        for vdc_vm in vdc_objects:
            if vdc_vm["fields"][8]["value"] == project["id"]:
                project_id_vdc_types[project["id"]] = {
                    "vdc_object_id": vdc_vm["public_id"]
                }

    projects: dict = checksum_vdc(portal_projects)

    del portal_projects

    dg_vdc_checksum = tuple(map(lambda x: {
        "vdc_id": x["name"],
        "type_id": x["public_id"],
        "check_sum": x["render_meta"]["sections"][0]["label"]
    }, dg_types))
    update_dg_types = list()

    for project in projects:
        for dg_vdc in dg_vdc_checksum:
            if project == dg_vdc["vdc_id"] and projects[project]["checksum"] != dg_vdc["check_sum"]:
                update_dg_types.append(
                    {
                        "type_id": dg_vdc["type_id"],
                        "vdc_id": dg_vdc["vdc_id"],
                        "networks": projects[project]["networks"]
                    }
                )

    logger.info(f"Vdc where there are changes = {len(update_dg_types)}")

    all_objects: tuple = get_mongodb_objects("framework.objects")

    for project in projects:
        if not any(tuple(map(lambda x: x['name'] == project, dg_types))):
            vdc_id: int = project_id_vdc_types[project]["vdc_object_id"]

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
                        "name": "network-name",
                        "label": "network name"
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
                        "name": "description",
                        "label": "description"
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
                        "type": "text",
                        "name": "record-update-time",
                        "label": "record update time"
                    },
                    {
                        "type": "ref",
                        "name": "vdc-link",
                        "label": "vdc link",
                        "ref_types": [
                            dg_vdc_type["public_id"]
                        ],
                        "summaries": [],
                        # "default": len(all_objects)
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
                                "network-name",
                                "summary-vm-info",
                                "local-ip",
                                "public-ip",
                                "tags",
                                "description",
                                "zone",
                                "ingress-ports",
                                "egress-ports",
                                "state",
                                "creator",
                                "vm-id",
                                "os-id",
                                "creation-date",
                                "record-update-time",
                                "vdc-link"
                            ],
                            "type": "section",
                            "name": "passport-vm-%s" % region,
                            "label": projects[project]["checksum"]
                        }
                    ],
                    "externals": [
                        {
                            "name": "vdc-link",
                            "href": f"{portal_info['url']}/client/orders/{project}",
                            "label": "Vdc Link",
                            "icon": "fas fa-external-link-alt",
                            "fields": []
                        },
                        {
                            "name": "vm-link",
                            "href": f"{portal_info['url']}/client/orders/{project}/servers/{{}}/info",
                            "label": "Vm Link",
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
                            "network-name",
                            "local-ip",
                            "public-ip",
                            "tags",
                            "description",
                            "state",
                            "creation-date",
                            "record-update-time",
                            "vdc-link"
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
                "name": project,
                "label": f"{projects[project]['name']} | {projects[project]['zone']} | {project}",
                "description": projects[project]['desc'] if 'desc' in projects[project] else "passport-vm-%s" % region
            }

            create_type: int = dg_api("POST", "types/", dg_token, payload_type_tmp)["result_id"]
            logger.info(f'Create new type {create_type}')

            dg_categories: tuple = get_mongodb_objects("framework.categories")

            # category_search: dict = max(filter(lambda y: y["name"] == "group_id--%s" % projects[project]["group_id"],
            #                                    dg_categories))

            category_search = None
            for group in dg_categories:
                if group["name"] == "group_id--%s" % projects[project]["group_id"]:
                    category_search = group
                    break

            if not category_search:
                raise RuntimeError("Group not fount")

            payload_category_tmp: dict = {
                "public_id": category_search["public_id"],
                "name": category_search["name"],
                "label": category_search["label"],
                "meta": {
                    "icon": "fas fa-folder-open",
                    "order": None
                },
                "parent": category_search["parent"],
                "types": category_search["types"]
            }

            payload_category_tmp["types"].append(create_type)

            dg_api("PUT", "categories/%s" % category_search["public_id"], dg_token, payload_category_tmp)
            logger.info(f'Put new type {create_type} in category {category_search["label"]}')

            vm_list: list = portal_api("servers?project_id=%s" % project)["stdout"]["servers"]

            for server in vm_list:
                create_object = vm_objects(server, create_type, projects[project]["networks"], vdc_object=vdc_id)
                logger.info(f'Create object {create_object} in {create_type}')

    if not update_dg_types:
        return all_objects

    for dg_type in update_dg_types:
        vdc_id: int = project_id_vdc_types[dg_type["vdc_id"]]["vdc_object_id"]
        vm_list: list = portal_api("servers?project_id=%s" % dg_type["vdc_id"])["stdout"]["servers"]

        dg_type_objects = tuple(filter(lambda x: x["type_id"] == dg_type["type_id"], all_objects))

        portal_project_vms = tuple(map(lambda server: vm_objects(server, dg_type["type_id"], dg_type["networks"],
                                                                 template=True, vdc_object=vdc_id)["fields"], vm_list))

        for portal_vm in portal_project_vms:
            if not any(map(lambda x: x["fields"][19]["value"] == portal_vm[19]["value"], dg_type_objects)):
                logger.info(f'Vm-object {portal_vm[2]["value"]} for creating in {dg_type["type_id"]}')
                vm_objects(portal_vm, dg_type["type_id"], dg_type["networks"], "POST_VM", vdc_object=vdc_id)

            for dg_object in dg_type_objects:
                dg_to_diff = dg_object["fields"].copy()
                tmp_to_diff = portal_vm.copy()
                dg_to_diff.pop(-2)
                tmp_to_diff.pop(-2)

                if dg_object["fields"][19]["value"] == portal_vm[19]["value"] and dg_to_diff != tmp_to_diff:
                    logger.info(f'Vm-object {portal_vm[2]["value"]} for updating in {dg_type["type_id"]}')
                    payload_object_tmp: dict = {
                        "type_id": dg_type["type_id"],
                        "status": dg_object["status"],
                        "version": dg_object["version"],
                        "creation_time": {
                            "$date": int(time.mktime(dg_object["creation_time"].timetuple()) * 1000)
                        },
                        "author_id": dg_object["author_id"],
                        "last_edit_time": {
                            "$date": int(time.time() * 1000)
                        },
                        "editor_id": user_id,
                        "active": dg_object["active"],
                        "fields": portal_vm,
                        "public_id": dg_object["public_id"],
                        "views": dg_object["views"],
                        "comment": ""
                    }

                    vm_objects(payload_object_tmp, dg_type["type_id"], dg_type["networks"], "PUT", vdc_object=vdc_id)

        for object in filter(
                lambda x: x[1][19]["value"] not in tuple(map(lambda x: x[19]["value"], portal_project_vms)),
                map(lambda y: (y.get("public_id"), y.get("fields")), dg_type_objects)):
            logger.info(f'Delete vm-object {object[1][0]["value"]}')
            dg_api("DELETE", "object/%s" % object[0], dg_token)

        get_info_dg_vdc = max(filter(lambda y: y["name"] == dg_type["vdc_id"], dg_types))

        get_info_dg_vdc["id"] = get_info_dg_vdc["name"]

        get_info_dg_vdc: dict = get_vdc_checksum(get_info_dg_vdc)

        del get_info_dg_vdc["info"]["id"], get_info_dg_vdc["info"]["_id"]
        get_info_dg_vdc["info"]["render_meta"]["sections"][0]["label"] = get_info_dg_vdc["checksum"]
        get_info_dg_vdc["info"]["last_edit_time"] = \
            time.strftime(f"%Y-%m-%dT%H:%M:%S.{str(time.time())[-5:]}0", time.localtime(time.time()))
        get_info_dg_vdc["info"]["creation_time"] = json_serial(get_info_dg_vdc["info"]["creation_time"])

        logger.info(f'Update checksum for {dg_type["type_id"]} in CMDB')
        dg_api("PUT", "types/%s" % dg_type["type_id"], dg_token, get_info_dg_vdc["info"])

    dg_categories: tuple = get_mongodb_objects("framework.categories")

    for dg_category in dg_categories:
        if "group_id--" in dg_category["name"] and not dg_category['types']:
            result: dict = dg_api("DELETE", "categories/%s" % dg_category["public_id"], dg_token)
            logger.info(f"Delete category {result['raw']['label']} from dg")

    return all_objects
