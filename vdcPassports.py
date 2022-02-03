#!/usr/bin/python3

import json
import time
from typing import Union, Tuple

import requests
import datetime
from functools import reduce
from collections import defaultdict
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from env import portal_info
from tools import *
from vm_passport import portalApi
from vm_passport import cmdbApi
from vm_passport import objects
from vm_passport import categorie_id
from vm_passport import getCmdbToken
from vm_passport import getInfoFromAllPage

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def PassportsVDC(portal_name: str, all_objects: tuple = ()) -> None:
    cmdb_token, user_id = getCmdbToken()
    allCategories = getInfoFromAllPage('categories', cmdb_token)

    vdc_categorie_id = categorie_id('passports-vdc', 'Passports VDC', 'fas fa-network-wired', cmdb_token,
                                    allCategories)

    # osPortalCategorieId = categorie_id(f'VDC-{portal_name}', f'VDC-{portal_name}', 'fas fa-folder-open',
    #                                    cmdb_token, allCategories, vdc_categorie_id['public_id'])

    def createVcd(vcd_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
                  template: bool = False) -> dict:
        if method == 'PUT':
            print(f'object/{vcd_info["public_id"]}')

        # "name",
        # "datacenter-name",
        # "networks",
        # "dns-nameservers",
        # "openstack-id",
        # "default-network",
        # "subnet-name",
        # "subnet-uuid",
        # "network-name",
        # "network-uuid"

        def networks_info(networks: list, dns_servers: bool, subnet: bool) -> str:# Union[str, tuple[str, str, str, str]]:
            networks = tuple(map(lambda x: defaultdict(str, x), networks))
            if dns_servers:
                dnsInfo = list()
                for network in networks:
                    dnsInfo.append(network['dns_nameservers'])
                return '\n'.join(map(lambda x: '\n'.join(x), dnsInfo))
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

        subnet_name, subnet_uuid, network_name, network_uuid = networks_info(vcd_info['networks'], False, True)

        payload_vcd_object: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "name",
                    "value": vcd_info["name"]
                },
                {
                    "name": "datacenter-name",
                    "value": vcd_info["datacenter_name"]
                },
                {
                    "name": "networks",
                    "value": networks_info(vcd_info["networks"], dns_servers=False, subnet=False)
                },
                {
                    "name": "dns-nameservers",
                    "value": networks_info(vcd_info["networks"], dns_servers=True, subnet=False)
                },
                {
                    "name": "openstack-id",
                    "value": vcd_info["openstack_project_id"]
                },
                {
                    "name": "default-network",
                    "value": vcd_info["default_network"]
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

        return cmdbApi("POST", "object/", cmdb_token, payload_vcd_object)
        # json_read(payload_vcd_object)

    dg_types: tuple = getInfoFromAllPage('types', cmdb_token)

    for i in dg_types:
        print(i)

    return

    portal_vdc: list = portalApi("projects", portal_name)["stdout"]["projects"]

    if not any(map(lambda x: any(map(lambda y: y["name"] == f"VDC-{portal_name}", x["results"])),
                   dg_types)):  # and cluster['cluster'] == 'ocp.bootcampsdp.tech':

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

        create_type = cmdbApi("POST", "types/", cmdb_token, payload_type_tmp)
        print(create_type)
        allTypesPages = getInfoFromAllPage("types", cmdb_token)[0]["pager"]["total_pages"]

        newAllTypesPages = list()
        for page in range(1, allTypesPages + 1):
            responsePage = cmdbApi("GET", f"types/?page={page}", cmdb_token)
            newAllTypesPages.append(responsePage)

        newTypeId = None
        for newTypes in newAllTypesPages:
            for newItem in newTypes['results']:
                if newItem['name'] == f"VDC-{portal_name}":
                    newTypeId = newItem['public_id']

        print(newTypeId, 'new type id')
        # osPortalCategorieId = categorie_id(f'OS-{portal_name}', f'OS-{portal_name}', 'far fa-folder-open',
        #                                       vdc_categorie_id['public_id'], allCategories)
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

        if newTypeId == None:
            return

        payload_categorie['types'].append(newTypeId)

        putTypeInCat = cmdbApi('PUT', f"categories/{vdc_categorie_id['public_id']}", cmdb_token,
                               payload_categorie)
        print('putTypeInCatigories', putTypeInCat)
        print('payload_categorie', payload_categorie)

        for vdc in portal_vdc:
            createObject = createVcd(vdc, cmdb_token, newTypeId, user_id)
            print(createObject)
            time.sleep(0.1)

    from allObjects import all_objects

    dg_types: tuple = getInfoFromAllPage('types', cmdb_token)
    dg_vdc_types = map(lambda z: tuple(filter(lambda f: f'VDC-{portal_name}' in f['name'], z['results'])), dg_types)
    del dg_types
    dg_vdc_types = reduce(lambda x, y: x + y, dg_vdc_types)
    jsonRead(dg_vdc_types)
    return

    for cmdbCluster in allCmdbClusterTypes:
        for cluster in os_info:
            if cmdbCluster['label'] == cluster['cluster']:
                # print(cmdbCluster['label'], cluster['cluster'])

                # cmdb_namespaces = tuple(filter(lambda f: f['type_id'] == cmdbCluster['public_id'],
                #                                reduce(lambda x, y: x + y, map(lambda z: tuple(
                #                                    map(lambda j: dict(public_id=j.get('public_id'),
                #                                                       type_id=j.get('type_id'),
                #                                                       author_id=j.get('author_id'),
                #                                                       fields=j.get('fields'),
                #                                                       creation_time=j.get('creation_time')),
                #                                        z['results'])), all_objects))))

                cmdbNamespaces = tuple(filter(lambda x: x['type_id'] == cmdbCluster['public_id'], all_objects))
                for osNamespace in cluster['info']:
                    if osNamespace['namespace'] not in map(lambda x: x.get('fields')[0]['value'], cmdbNamespaces):
                        print('NAMESPACE FOR CREATE', osNamespace['namespace'])
                        objects(osNamespace, cmdb_token, cmdbCluster['public_id'], user_id, 'NAMESPACE')
                        time.sleep(0.1)

                    for cmdbNs in cmdbNamespaces:
                        nsTemplate = objects(osNamespace, cmdb_token, cmdbCluster['public_id'], user_id,
                                             'NAMESPACE', template=True)
                        if cmdbNs['fields'][0]['value'] == osNamespace['namespace'] and cmdbNs['fields'] != \
                                nsTemplate['fields']:
                            # unixTime = lambda x: int(datetime.datetime.timestamp(x) * 1000)
                            # print(unixTime(cmdbNs['creation_time']))

                            updateObjectTemplate: dict = {
                                "type_id": cmdbNs['type_id'],
                                "status": True,
                                "version": "1.0.1",
                                "creation_time": {
                                    # "$date": int(time.mktime(time.strptime(cmdbNs['creation_time'], '%Y-%m-%dT%H:%M:%S.%f')) * 1000)
                                    "$date": int(datetime.datetime.timestamp(cmdbNs['creation_time']) * 1000)
                                },
                                "author_id": cmdbNs['author_id'],
                                "last_edit_time": {
                                    "$date": int(time.time() * 1000)
                                },
                                "editor_id": user_id,
                                "active": True,
                                "fields": nsTemplate['fields'],
                                "public_id": cmdbNs['public_id'],
                                "views": 0,
                                "comment": ""
                            }

                            # json_read(updateObjectTemplate)
                            time.sleep(0.1)
                            print(f"UPDATE NAMESPACE in {cmdbNs['type_id']}", osNamespace['namespace'])
                            objects(updateObjectTemplate, cmdb_token, cmdbCluster['public_id'], user_id, 'PUT')

                for cmdbNs in cmdbNamespaces:
                    if cmdbNs['fields'][0]['value'] not in map(lambda x: x['namespace'], cluster['info']):
                        print('DELETE NAMESPACE', cmdbNs['fields'][0]['value'])
                        cmdbApi('DELETE', f"object/{cmdbNs['public_id']}", cmdb_token)
                        time.sleep(0.1)


if __name__ == '__main__':
    PassportsVDC('PD15')

# "name",
# "datacenter-name",
# "networks",
# "dns-nameservers",
# "openstack-id",
# "default-network",
# "subnet-name",
# "subnet-uuid",
# "network-name",
# "network-uuid"
