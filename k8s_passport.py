#!/usr/local/bin/python3

import time
from loguru import logger
from datetime import datetime

from env import portal_info
from common_function import dg_api, category_id, get_mongodb_objects, get_k8s_info


def passports_k8s(region: str, auth_info: tuple, all_objects: tuple = ()) -> None:
    if portal_info["metrics"] == "false":
        return

    dg_token, user_id = auth_info

    def ns_objects(ns_info: dict, type_id: int, method: str = "POST", template: bool = False) -> dict:
        """
        Func to create or update or delete ns_objects in DataGerry
        :param ns_info:
        :param type_id:
        :param method:
        :param template:
        :return:
        """
        if method == "PUT":
            return dg_api(method, "object/%s" % ns_info["public_id"], dg_token, ns_info)

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
            "author_id": user_id,
            "fields": [
                {
                    "name": "namespace",
                    "value": ns_info["namespace"]
                },
                {
                    "name": "limits-cpu-hard",
                    "value": get_metric(ns_info["info"], "limits.cpu", "hard")
                },
                {
                    "name": "limits-cpu-used",
                    "value": get_metric(ns_info["info"], "limits.cpu", "used")
                },
                {
                    "name": "cores-usage",
                    "value": get_usage(get_metric(ns_info["info"], "limits.cpu", "used"),
                                       get_metric(ns_info["info"], "limits.cpu", "hard"))
                },
                {
                    "name": "limits-memory-hard",
                    "value": fract(convert_to_gb(get_metric(ns_info["info"], "limits.memory", "hard")))
                },
                {
                    "name": "limits-memory-used",
                    "value": fract(convert_to_gb(get_metric(ns_info["info"], "limits.memory", "used")))
                },
                {
                    "name": "memory-usage",
                    "value": get_usage(get_metric(ns_info["info"], "limits.memory", "used"),
                                       get_metric(ns_info["info"], "limits.memory", "hard"))
                },
                {
                    "name": "record-update-time",
                    "value": datetime.now().strftime("%d.%m.%Y %H:%M")
                }
            ]
        }

        if template:
            return payload_ns_tmp

        return dg_api("POST", "object/", dg_token, payload_ns_tmp)

    dg_categories: tuple = get_mongodb_objects("framework.categories")

    k8s_passports_category_id: dict = category_id("passports-k8s", "Passports K8s", "fab fa-redhat", dg_token,
                                                  dg_categories)
    k8s_region_category_id: dict = category_id("k8s-%s" % region, "K8s-%s" % region.upper(), "far fa-folder-open",
                                               dg_token, dg_categories, k8s_passports_category_id["public_id"])

    cluster_info: list = get_k8s_info()

    #### temporary
    def clear_info(old_info: list) -> list:
        new_info = list()
        for info in old_info:
            if "cluster" in info["metric"] and "namespace" in info["metric"] and "resource" in info["metric"]:
                # if "cluster" in info["metric"] and "namespace" in info["metric"]:
                new_info.append(info)
        return new_info

    # clusters = tuple(map(lambda x: x["metric"]["cluster"], cluster_info))
    clusters = set([cluster['metric']['cluster'] for cluster in cluster_info])

    k8s_info = list()
    for cluster in clusters:
        metrics = list()
        k8s_info.append(dict(cluster=cluster, info=metrics))
        for info in cluster_info:
            if cluster == info["metric"]["cluster"]:
                metrics.append(info["metric"]["namespace"])

    for info in k8s_info:
        info["info"] = list(set(info["info"]))
        i = -1
        for namespace in info["info"]:
            i += 1
            info["info"][i] = dict(namespace=namespace, info=list())

    for item in k8s_info:
        for info in item["info"]:
            for metric in cluster_info:
                if item["cluster"] == metric["metric"]["cluster"] and \
                        info["namespace"] == metric["metric"]["namespace"]:
                    info["info"].append((metric["metric"]["resource"], metric["metric"]["type"], metric["value"]))

    dg_projects: tuple = get_mongodb_objects("framework.types")

    def create_link_k8s(cluster: dict, type_id: int, method: str = "POST", template: bool = False) -> dict | str:
        if method == "PUT":
            return dg_api(method, "object/%s" % type_id, dg_token, cluster)

        payload_k8s_object: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": user_id,
            "fields": [
                {
                    "name": "name",
                    "value": cluster
                },
                {
                    "name": "record-update-time",
                    "value": datetime.now().strftime("%d.%m.%Y %H:%M")
                }
            ]
        }

        if template:
            return payload_k8s_object

        return dg_api("POST", "object/", dg_token, payload_k8s_object)

    search_link_type = False

    all_objects: tuple = get_mongodb_objects("framework.objects")

    for dg_type in dg_projects:
        if dg_type["name"] == "links-k8s-%s" % region:
            search_link_type = True

            all_k8s_objects = tuple(filter(lambda x: x["type_id"] == dg_type["public_id"], all_objects))

            for dg_object in all_k8s_objects:
                if dg_object["fields"][0]["value"] not in tuple(map(lambda x: x["cluster"], k8s_info)):
                    dg_api("DELETE", "object/%s" % dg_object["public_id"], dg_token)
                    logger.info(
                        f'Delete k8s cluster {dg_object["fields"][0]["value"]} from type {dg_type["public_id"]}'
                    )

            for cluster in k8s_info:
                for dg_object in all_k8s_objects:
                    vdc_template: dict = create_link_k8s(cluster["cluster"], dg_type["public_id"], template=True)

                    dg_to_diff = dg_object["fields"].copy()
                    tmp_to_diff = vdc_template["fields"].copy()
                    dg_to_diff.pop(-1)
                    tmp_to_diff.pop(-1)

                    if cluster["cluster"] == dg_object["fields"][0]["value"] and dg_to_diff != tmp_to_diff:
                        payload_link_tmp: dict = {
                            "type_id": dg_object["type_id"],
                            "status": dg_object["status"],
                            "version": dg_object["version"],
                            "creation_time": {
                                "$date": int(datetime.timestamp(dg_object["creation_time"]) * 1000)
                            },
                            "author_id": dg_object["author_id"],
                            "last_edit_time": {
                                "$date": int(time.time() * 1000)
                            },
                            "editor_id": user_id,
                            "active": dg_object["active"],
                            "fields": vdc_template["fields"],
                            "public_id": dg_object["public_id"],
                            "views": dg_object["views"],
                            "comment": ""
                        }

                        create_link_k8s(payload_link_tmp, dg_object["public_id"], "PUT")
                        logger.info(f'Update object {dg_object["public_id"]} in type {dg_object["type_id"]}')

                if cluster["cluster"] not in tuple(map(lambda x: x["fields"][0]["value"], all_k8s_objects)):
                    # all_vdc_objects.append({})
                    create_link_k8s(cluster["cluster"], dg_type["public_id"])
                    logger.info(f'Create vdc {cluster["cluster"]} in type {dg_type["public_id"]}')

            # all_objects: tuple = get_mongodb_objects("framework.objects")
            # all_vdc_objects = tuple(filter(lambda x: x["type_id"] == dg_vdc_type["public_id"], all_objects))

    if not search_link_type:
        payload_type_tmp: dict = {
            "fields": [
                {
                    "type": "text",
                    "name": "name",
                    "label": "name"
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
                # "icon": "fas fa-link",
                "icon": "fas fa-dharmachakra",
                "sections": [
                    {
                        "fields": [
                            "name",
                            "record-update-time"
                        ],
                        "type": "section",
                        "name": "links-k8s-%s" % region,
                        "label": "Links-k8s-%s" % region.upper()
                    }
                ],
                "externals": [],
                # "externals": [
                #     {
                #         "name": "cluster link",
                #         "href": "https://console-openshift-console.apps.{}/k8s/cluster/projects",
                #         "label": "Cluster link",
                #         "icon": "fas fa-external-link-alt",
                #         "fields": ["name"]
                #     },
                #
                # ],
                "summary": {
                    "fields": [
                        "name",
                        "record-update-time"
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
            "name": "links-k8s-%s" % region,
            "label": "Links-k8s-%s" % region.upper(),
            "description": "Links-k8s-%s" % region.upper()
        }

        create_type_id: int = dg_api("POST", "types/", dg_token, payload_type_tmp)["result_id"]

        if not create_type_id:
            return None

        logger.info(f"Create new type with id -> {create_type_id}")

        payload_category: dict = {
            # "public_id": links_category_id["public_id"],
            "public_id": k8s_region_category_id["public_id"],
            # "name": links_category_id["name"],
            "name": k8s_region_category_id["name"],
            # "label": links_category_id["label"],
            "label": k8s_region_category_id["label"],
            "meta": {
                "icon": "fab fa-staylinked",
                "order": None
            },
            # "parent": portal_stands_id["public_id"],
            # "types": links_category_id["types"]
            "types": k8s_region_category_id["types"]
        }

        payload_category["types"].append(create_type_id)

        # move_type = dg_api("PUT", "categories/%s" % links_category_id["public_id"], dg_token, payload_category)
        move_type = dg_api("PUT", "categories/%s" % k8s_region_category_id["public_id"], dg_token, payload_category)

        logger.info(f'Move type {move_type["result"]["public_id"]} to category {payload_category["name"]}')

        for cluster in k8s_info:
            link_k8s_object = create_link_k8s(cluster["cluster"], create_type_id)
            logger.info(f"Create vdc object {link_k8s_object} in {create_type_id}")

    for cluster in k8s_info:
        search_cluster = False
        for dg_project in dg_projects:
            if dg_project['name'] == f'k8s-cluster-{region}--{cluster["cluster"].replace(".", "_")}':
                search_cluster = True
                break

        if not search_cluster:
            # if not any(tuple(map(lambda y: y["name"] == f'k8s-cluster-{region}--{cluster["cluster"].replace(".", "_")}',
            #                      dg_projects))):
            data_type_tmp: dict = {
                "fields": [
                    {
                        "type": "text",
                        "name": "namespace",
                        "label": "namespace"
                    },
                    {
                        "type": "text",
                        "name": "limits-cpu-hard",
                        "label": "limits.cpu-hard"
                    },
                    {
                        "type": "text",
                        "name": "limits-cpu-used",
                        "label": "limits.cpu-used"
                    },
                    {
                        "type": "text",
                        "name": "cores-usage",
                        "label": "cores usage (%)"
                    },
                    {
                        "type": "text",
                        "name": "limits-memory-hard",
                        "label": "limits.memory-hard (Gi)"
                    },
                    {
                        "type": "text",
                        "name": "limits-memory-used",
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
                                "limits-cpu-hard",
                                "limits-cpu-used",
                                "cores-usage",
                                "limits-memory-hard",
                                "limits-memory-used",
                                "memory-usage",
                                "record-update-time"
                            ],
                            "type": "section",
                            "name": f"k8s-cluster-{region}--{cluster['cluster']}",
                            "label": cluster["cluster"]
                        }
                    ],
                    "externals": [],
                    # "externals": [
                    #     {
                    #         "name": "cluster-link",
                    #         "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects" % cluster[
                    #             "cluster"],
                    #         "label": "Cluster link",
                    #         "icon": "fas fa-external-link-alt",
                    #         "fields": []
                    #     },
                    #     {
                    #         "name": "namespace-link",
                    #         "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects/{}" % cluster[
                    #             "cluster"],
                    #         "label": "Namespace link",
                    #         "icon": "fas fa-external-link-alt",
                    #         "fields": ["namespace"]
                    #     }
                    # ],
                    "summary": {
                        "fields": [
                            "namespace",
                            "limits-cpu-hard",
                            "limits-cpu-used",
                            "cores-usage",
                            "limits-memory-hard",
                            "limits-memory-used",
                            "memory-usage",
                            "record-update-time"
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
                "name": f"k8s-cluster-{region}--{cluster['cluster'].replace('.', '_')}",
                "label": cluster["cluster"],
                "description": "k8s cluster %s" % cluster["cluster"]
            }

            create_type = dg_api("POST", "types/", dg_token, data_type_tmp)

            logger.info(f'Create new type {create_type["result_id"]} with id')

            data_category_tmp: dict = {
                "public_id": k8s_region_category_id["public_id"],
                "name": k8s_region_category_id["name"],
                "label": k8s_region_category_id["label"],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": k8s_passports_category_id["public_id"],
                "types": k8s_region_category_id["types"]
            }

            if not create_type["result_id"]:
                return

            data_category_tmp["types"].append(create_type["result_id"])

            dg_api("PUT", "categories/%s" % k8s_region_category_id["public_id"], dg_token, data_category_tmp)
            logger.info(f'Put new type {create_type["result_id"]} in category {data_category_tmp["name"]}')

            for namespace in cluster["info"]:
                ns_objects(namespace, create_type["result_id"])

    for dg_project in dg_projects:
        if dg_project['name'][:14 + len(region)] == f"k8s-cluster-{region}--":
            if dg_project['name'][14 + len(region):].replace("_", ".") not in clusters:
                logger.info(f"Delete k8s cluster {dg_project['label']} type from DG")
                dg_api("DELETE", "types/%s" % dg_project["public_id"], dg_token)

    if not all_objects:
        all_objects: tuple = get_mongodb_objects("framework.objects")

    all_dg_cluster_types = tuple(filter(lambda f: "k8s-cluster-%s--" % region in f["name"], dg_projects))

    for dg_cluster in all_dg_cluster_types:
        for cluster in k8s_info:
            if dg_cluster["label"] == cluster["cluster"]:
                dg_ns = tuple(filter(lambda x: x["type_id"] == dg_cluster["public_id"], all_objects))
                for k8s_ns in cluster["info"]:
                    if k8s_ns["namespace"] not in tuple(map(lambda x: x.get("fields")[0]["value"], dg_ns)):
                        logger.info(f'Create ns-object {k8s_ns["namespace"]}')
                        ns_objects(k8s_ns, dg_cluster["public_id"])

                    for ns in dg_ns:
                        ns_template = ns_objects(k8s_ns, dg_cluster["public_id"], template=True)
                        dg_to_diff = ns["fields"].copy()
                        tmp_to_diff = ns_template["fields"].copy()
                        dg_to_diff.pop(-1)
                        tmp_to_diff.pop(-1)

                        if ns["fields"][0]["value"] == k8s_ns["namespace"] and dg_to_diff != tmp_to_diff:
                            update_object_template: dict = {
                                "type_id": ns["type_id"],
                                "status": ns["version"],
                                "version": ns["version"],
                                "creation_time": {
                                    "$date": int(datetime.timestamp(ns["creation_time"]) * 1000)
                                },
                                "author_id": ns["author_id"],
                                "last_edit_time": {
                                    "$date": int(time.time() * 1000)
                                },
                                "editor_id": user_id,
                                "active": ns["active"],
                                "fields": ns_template["fields"],
                                "public_id": ns["public_id"],
                                "views": ns["views"],
                                "comment": ""
                            }

                            logger.info(f'Update ns-object {k8s_ns["namespace"]} in {ns["type_id"]}')
                            ns_objects(update_object_template, dg_cluster["public_id"], "PUT")

                for ns in dg_ns:
                    if ns["fields"][0]["value"] not in tuple(map(lambda x: x["namespace"], cluster["info"])):
                        logger.info(f'Delete ns-object {ns["fields"][0]["value"]}')
                        dg_api("DELETE", "object/%s" % ns["public_id"], dg_token)
