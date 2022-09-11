#!/usr/local/bin/python3

import json
import time
import requests
from loguru import logger
from datetime import datetime

from env import portal_info
from common_function import cmdb_api, \
    category_id, \
    get_dg_token, \
    get_mongodb_objects


def ns_objects(ns_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = "POST",
               template: bool = False) -> dict:
    """
    Func to create or update or delete ns_objects in DataGerry
    :param ns_info:
    :param cmdb_token:
    :param type_id:
    :param author_id:
    :param method:
    :param template:
    :param tags:
    :param vdc_object:
    :return:
    """
    if method == "PUT":
        return cmdb_api(method, "object/%s" % ns_info["public_id"], cmdb_token, ns_info)

    # elif method == "NAMESPACE":
    def convert_to_gb(bytes):
        foo = float(bytes)
        for i in range(3):
            foo = foo / 1024
        return foo

    def get_metric(ns_info: list, looking_metric: str, type_metric: str) -> str:
        for metric in ns_info:
            if metric[0] == looking_metric and metric[1] == type_metric:
                return metric[2][1]

    # metric = lambda x, y: filter(lambda foo: foo[2][1] if foo[0] == x and foo[1] == y else None, ns_info["info"])

    # get_usage = lambda x, y: "%.2f" % ((float(x) / float(y)) * 100) if float(y) != 0.0 else str(float(y))

    def get_usage(x: str, y: str) -> str:
        return "%.2f" % ((float(x) / float(y)) * 100) if float(y) != 0.0 else str(float(y))

    # fract = lambda x: str(int(x)) if x - int(x) == 0 else "%.2f" % x

    def fract(x: float) -> str:
        return str(int(x)) if x - int(x) == 0 else "%.2f" % x

    payload_ns_tmp: dict = {
        "status": True,
        "type_id": type_id,
        "version": "1.0.0",
        "author_id": author_id,
        "fields": [
            {
                "name": "namespace",
                "value": ns_info["namespace"]
            },
            {
                "name": "limits.cpu-hard",
                "value": get_metric(ns_info["info"], "limits.cpu", "hard")
            },
            {
                "name": "limits.cpu-used",
                "value": get_metric(ns_info["info"], "limits.cpu", "used")
            },
            {
                "name": "cores-usage",
                "value": get_usage(get_metric(ns_info["info"], "limits.cpu", "used"),
                                   get_metric(ns_info["info"], "limits.cpu", "hard"))
            },
            {
                "name": "limits.memory-hard",
                "value": fract(convert_to_gb(get_metric(ns_info["info"], "limits.memory", "hard")))
            },
            {
                "name": "limits.memory-used",
                "value": fract(convert_to_gb(get_metric(ns_info["info"], "limits.memory", "used")))
            },
            {
                "name": "memory-usage",
                "value": get_usage(get_metric(ns_info["info"], "limits.memory", "used"),
                                   get_metric(ns_info["info"], "limits.memory", "hard"))
            },
            {
                "name": "record-update-time",
                "value": datetime.now().strftime('%d.%m.%Y %H:%M')
            }
        ]
    }

    if template:
        return payload_ns_tmp

    return cmdb_api("POST", "object/", cmdb_token, payload_ns_tmp)

    # print(response.status_code)
    # print(response.json())
    # try:
    #     return cmdb_api("POST", "object/", cmdb_token, payload_vm_tmp)
    # except:
    #     number_of_recursions += 1
    #     if response["status_code"] != 201 and number_of_recursions != 5:
    #         time.sleep(1)
    #         print(f"Status Code {response["status_code"]}")
    #         put_tag(ns_info, number_of_recursions)
    #     return dict(vm_name=ns_info["name"], tag_name=ns_info["tag_name"], status_code=response["status_code"])


def PassportsOS(portal_name: str, all_objects: tuple = None) -> None:
    if portal_info[portal_name]["metrics"] == "false":
        return

    cmdb_token, user_id = get_dg_token()

    all_categories: tuple = get_mongodb_objects("framework.categories")

    os_passports_category_id: dict = \
        category_id("passports-k8s", "Passports K8s", "fab fa-redhat", cmdb_token, all_categories)
    os_portal_category_id: dict = category_id("K8s-%s" % portal_name, "K8s-%s" % portal_name, "far fa-folder-open",
                                              cmdb_token, all_categories, os_passports_category_id["public_id"])

    def get_os_info() -> dict:
        return json.loads(requests.request("GET", portal_info[portal_name]["metrics"]).content)

    cluster_info: dict = get_os_info()

    #### temporary
    def clear_info(old_info: list) -> list:
        new_info = list()
        for info in old_info:
            if "cluster" in info["metric"] and "namespace" in info["metric"] and "resource" in info["metric"]:
            # if "cluster" in info["metric"] and "namespace" in info["metric"]:
                new_info.append(info)
        return new_info

    # cluster_info["data"]["result"] = tuple(map(lambda x: {'metric': defaultdict(str, x['metric'])},
    #                                            cluster_info["data"]["result"]))
    cluster_info["data"]["result"] = clear_info(cluster_info["data"]["result"])
    #### temporary
    clusters = tuple(map(lambda x: x["metric"]["cluster"], cluster_info["data"]["result"]))

    os_info = list()
    for cluster in set(clusters):
        metrics = list()
        os_info.append(dict(cluster=cluster, info=metrics))
        for info in cluster_info["data"]["result"]:
            if cluster == info["metric"]["cluster"]:
                metrics.append(info["metric"]["namespace"])

    for info in os_info:
        info["info"] = list(set(info["info"]))
        i = -1
        for namespace in info["info"]:
            i += 1
            info["info"][i] = dict(namespace=namespace, info=list())

    for item in os_info:
        for info in item["info"]:
            for metric in cluster_info["data"]["result"]:
                if item["cluster"] == metric["metric"]["cluster"] and \
                        info["namespace"] == metric["metric"]["namespace"]:
                    info["info"].append((metric["metric"]["resource"], metric["metric"]["type"], metric["value"]))

    cmdb_projects: tuple = get_mongodb_objects("framework.types")

    for cluster in os_info:
        if not any(tuple(map(lambda y: y["name"] == f"os-cluster-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                             cmdb_projects))):

            data_type_template: dict = {
                "fields": [
                    {
                        "type": "text",
                        "name": "namespace",
                        "label": "namespace"
                    },
                    {
                        "type": "text",
                        "name": "limits.cpu-hard",
                        "label": "limits.cpu-hard"
                    },
                    {
                        "type": "text",
                        "name": "limits.cpu-used",
                        "label": "limits.cpu-used"
                    },
                    {
                        "type": "text",
                        "name": "cores-usage",
                        "label": "cores usage (%)"
                    },
                    {
                        "type": "text",
                        "name": "limits.memory-hard",
                        "label": "limits.memory-hard (Gi)"
                    },
                    {
                        "type": "text",
                        "name": "limits.memory-used",
                        "label": "limits.memory-used (Gi)"
                    },
                    {
                        "type": "text",
                        "name": "memory-usage",
                        "label": "memory usage (%)"
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
                    # "icon": "fas fa-clipboard-list",
                    "icon": "fas fa-dharmachakra",
                    "sections": [
                        {
                            "fields": [
                                "namespace",
                                "limits.cpu-hard",
                                "limits.cpu-used",
                                "cores-usage",
                                "limits.memory-hard",
                                "limits.memory-used",
                                "memory-usage",
                                "record-update-time"
                            ],
                            "type": "section",
                            "name": f"os-cluster-{portal_name}--{cluster['cluster']}",
                            "label": cluster["cluster"]
                        }
                    ],
                    "externals": [
                        {
                            "name": "cluster link",
                            "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects" %
                                    cluster["cluster"],
                            "label": "Cluster link",
                            "icon": "fas fa-external-link-alt",
                            "fields": []
                        },
                        {
                            "name": "namespace link",
                            "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects/{}" %
                                    cluster["cluster"],
                            "label": "Namespace link",
                            "icon": "fas fa-external-link-alt",
                            "fields": ["namespace"]
                        }
                    ],
                    "summary": {
                        "fields": [
                            "namespace",
                            "limits.cpu-hard",
                            "limits.cpu-used",
                            "cores-usage",
                            "limits.memory-hard",
                            "limits.memory-used",
                            "memory-usage"
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
                "name": f"os-cluster-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                "label": cluster["cluster"],
                "description": "openshift cluster %s" % cluster["cluster"]
            }

            create_type = cmdb_api("POST", "types/", cmdb_token, data_type_template)

            logger.info(f'Create new type {create_type["result_id"]} with id')

            data_category_template: dict = {
                "public_id": os_portal_category_id["public_id"],
                "name": os_portal_category_id["name"],
                "label": os_portal_category_id["label"],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": os_passports_category_id["public_id"],
                "types": os_portal_category_id["types"]
            }

            if not create_type["result_id"]:
                return

            data_category_template["types"].append(create_type["result_id"])

            cmdb_api("PUT", "categories/%s" % os_portal_category_id["public_id"], cmdb_token, data_category_template)
            logger.info(f'Put new type {create_type["result_id"]} in category {data_category_template["name"]}')

            for namespace in cluster["info"]:
                create_object = ns_objects(namespace, cmdb_token, create_type["result_id"], user_id, "NAMESPACE")
                print(create_object)
                time.sleep(0.1)

    if not all_objects:
        all_objects: tuple = get_mongodb_objects("framework.objects")

    all_cmdb_cluster_types = tuple(filter(lambda f: "os-cluster-%s--" % portal_name in f["name"], cmdb_projects))

    for cmdb_cluster in all_cmdb_cluster_types:
        for cluster in os_info:
            if cmdb_cluster["label"] == cluster["cluster"]:
                cmdb_namespaces = tuple(filter(lambda x: x["type_id"] == cmdb_cluster["public_id"], all_objects))
                for os_namespace in cluster["info"]:
                    if os_namespace["namespace"] not in tuple(map(lambda x: x.get("fields")[0]["value"],
                                                                  cmdb_namespaces)):
                        logger.info(f'Create ns-object {os_namespace["namespace"]}')
                        ns_objects(os_namespace, cmdb_token, cmdb_cluster["public_id"], user_id, "NAMESPACE")
                        time.sleep(0.1)

                    for cmdb_ns in cmdb_namespaces:
                        ns_template = ns_objects(os_namespace, cmdb_token, cmdb_cluster["public_id"], user_id,
                                                 template=True)
                        if cmdb_ns["fields"][0]["value"] == os_namespace["namespace"] and cmdb_ns["fields"] != \
                                ns_template["fields"]:
                            update_object_template: dict = {
                                "type_id": cmdb_ns["type_id"],
                                "status": cmdb_ns["version"],
                                "version": cmdb_ns["version"],
                                "creation_time": {
                                    "$date": int(datetime.datetime.timestamp(cmdb_ns["creation_time"]) * 1000)
                                },
                                "author_id": cmdb_ns["author_id"],
                                "last_edit_time": {
                                    "$date": int(time.time() * 1000)
                                },
                                "editor_id": user_id,
                                "active": cmdb_ns["active"],
                                "fields": ns_template["fields"],
                                "public_id": cmdb_ns["public_id"],
                                "views": cmdb_ns["views"],
                                "comment": ""
                            }

                            time.sleep(0.1)
                            logger.info(f'Update ns-object {os_namespace["namespace"]} in {cmdb_ns["type_id"]}')
                            ns_objects(update_object_template, cmdb_token, cmdb_cluster["public_id"], user_id, "PUT")

                for cmdb_ns in cmdb_namespaces:
                    if cmdb_ns["fields"][0]["value"] not in tuple(map(lambda x: x["namespace"], cluster["info"])):
                        logger.info(f'Delete ns-object {cmdb_ns["fields"][0]["value"]}')
                        cmdb_api("DELETE", "object/%s" % cmdb_ns["public_id"], cmdb_token)
                        time.sleep(0.1)
