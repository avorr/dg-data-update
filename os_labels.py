#!/usr/local/bin/python3

import time
import socket
import requests
from loguru import logger
from itertools import zip_longest

from tools import *
from env import portal_info
from common_function import get_mongodb_objects, \
    get_dg_token, \
    category_id, \
    cmdb_api


def LabelsOS(portal_name: str, all_objects: tuple = ()) -> None:
    """
    main func for autocomplete labels in DataGerry
    :param portal_name:
    :param all_objects:
    :return:
    """
    if portal_info[portal_name]["metrics"] == "false":
        return

    def create_label(labels_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = "POST",
                     template: bool = False) -> dict:
        """
        func to create or update or delete label objects in DataGerry CMDB
        :param labels_info:
        :param cmdb_token:
        :param type_id:
        :param author_id:
        :param method:
        :param template:
        :return:
        """

        if method == "PUT":
            return cmdb_api(method, "object/%s" % labels_info["public_id"], cmdb_token, labels_info)

        def get_label(labels: dict, label: str) -> str:
            """
            Func to get labels from ose exporter
            :param labels:
            :param label:
            :return:
            """
            if "labels" in labels:
                if label in labels:
                    return labels[label]
                elif label in labels["labels"]:
                    return labels["labels"][label]
                else:
                    return ""
            else:
                if label in labels:
                    return labels[label]
                else:
                    return ""

        label_object_template: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "namespace",
                    "value": get_label(labels_info, "namespace")
                },
                {
                    "name": "name",
                    "value": get_label(labels_info, "name")
                },
                {
                    "name": "app",
                    "value": get_label(labels_info, "app")
                },
                {
                    "name": "SUBSYSTEM",
                    "value": get_label(labels_info, "SUBSYSTEM")

                },
                {
                    "name": "deployment",
                    "value": get_label(labels_info, "deployment")
                },
                {
                    "name": "deploymentconfig",
                    "value": get_label(labels_info, "deploymentconfig")
                },
                {
                    "name": "deployDate",
                    "value": get_label(labels_info, "deployDate")
                },
                {
                    "name": "distribVersion",
                    "value": get_label(labels_info, "distribVersion")
                },
                {
                    "name": "version",
                    "value": get_label(labels_info, "version")
                },
                {
                    "name": "build",
                    "value": get_label(labels_info, "build")
                },
                {
                    "name": "restartPolicy",
                    "value": get_label(labels_info, "restartPolicy")
                },
                {
                    "name": "imagePullPolicy",
                    "value": get_label(labels_info, "imagePullPolicy")
                },
                {
                    "name": "image",
                    "value": get_label(labels_info, "image")
                },
                {
                    "name": "security.istio.io/tlsMode",
                    "value": get_label(labels_info, "security.istio.io/tlsMode")
                },
                {
                    "name": "jenkinsDeployUser",
                    "value": get_label(labels_info, "jenkinsDeployUser")
                }
            ]
        }

        if template:
            return label_object_template

        return cmdb_api("POST", "object/", cmdb_token, label_object_template)

    cmdb_token, user_id = get_dg_token()

    all_categories: tuple = get_mongodb_objects("framework.categories")

    os_passports_category_id: dict = category_id("k8s-apps-labels", "K8s Apps Labels", "fas fa-tags",
                                                 cmdb_token, all_categories)

    os_portal_category_id: dict = category_id("K8s-Labels-%s" % portal_name, "K8s-Labels-%s" % portal_name,
                                              "fas fa-folder-open", cmdb_token, all_categories,
                                              os_passports_category_id["public_id"])

    def get_os_info() -> dict:
        """
        Func to get json from ose exporter
        :return:
        """
        return json.loads(requests.request("GET", portal_info[portal_name]["metrics"]).content)

    cluster_info: dict = get_os_info()

    #### temporary
    def clear_info(old_info: list) -> list:
        new_info = list()
        for info in old_info:
            if "cluster" in info["metric"]:
                new_info.append(info)
        return new_info

    cluster_info["data"]["result"]: list = clear_info(cluster_info["data"]["result"])
    #### temporary

    clusters = tuple(map(lambda x: x["metric"]["cluster"], cluster_info["data"]["result"]))

    def get_ose_labels(clusters: map) -> list:
        """
        function for getting pod labels from all clusters
        :param clusters:
        :return: list
        """

        def check_resolves(dns_name: str) -> bool:
            """
            function for checking resolving dns names
            :param dns_name:
            :return: bool
            """
            try:
                socket.gethostbyname(dns_name)
                return True
            except socket.error as Error:
                print(dns_name, Error)
                return False

        def check_port(checked_host: str, port: int) -> bool:
            """
            function to check server's port availability
            :param checked_host:
            :return: bool
            """
            if not checked_host:
                return False
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                return s.connect_ex((checked_host, port)) == 0

        all_labels = list()
        for cluster_name in set(clusters):
            if check_resolves("query-runner.apps.%s" % cluster_name) and \
                    check_port("query-runner.apps.%s" % cluster_name, 443):
                get_labels = requests.request("GET", "https://query-runner.apps.%s/pods" % cluster_name, verify=False)
                if get_labels.status_code == 200:
                    all_labels.append(dict(cluster=cluster_name, labels=json.loads(get_labels.content)))

        return all_labels

    all_labels: list = get_ose_labels(clusters)

    cmdb_projects: tuple = get_mongodb_objects("framework.types")

    for cluster in all_labels:
        if not any(tuple(map(lambda y: y["name"] == f'k8s-labels-{portal_name}--{cluster["cluster"].replace(".", "_")}',
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
                        "name": "name",
                        "label": "name"
                    },
                    {
                        "type": "text",
                        "name": "app",
                        "label": "app"
                    },
                    {
                        "type": "text",
                        "name": "SUBSYSTEM",
                        "label": "SUBSYSTEM"
                    },
                    {
                        "type": "text",
                        "name": "deployment",
                        "label": "deployment"
                    },
                    {
                        "type": "text",
                        "name": "deploymentconfig",
                        "label": "deploymentconfig"
                    },
                    {
                        "type": "text",
                        "name": "deployDate",
                        "label": "deployDate"
                    },
                    {
                        "type": "text",
                        "name": "distribVersion",
                        "label": "distribVersion"
                    },
                    {
                        "type": "text",
                        "name": "version",
                        "label": "version"
                    },
                    {
                        "type": "text",
                        "name": "build",
                        "label": "build"
                    },
                    {
                        "type": "text",
                        "name": "restartPolicy",
                        "label": "restartPolicy"
                    },
                    {
                        "type": "text",
                        "name": "imagePullPolicy",
                        "label": "imagePullPolicy"
                    },
                    {
                        "type": "text",
                        "name": "image",
                        "label": "image"
                    },
                    {
                        "type": "text",
                        "name": "security.istio.io/tlsMode",
                        "label": "security.istio.io/tlsMode"
                    },
                    {
                        "type": "text",
                        "name": "jenkinsDeployUser",
                        "label": "jenkinsDeployUser"
                    }
                ],
                "active": True,
                "version": "1.0.0",
                "author_id": user_id,
                "render_meta": {
                    "icon": "fas fa-dharmachakra",
                    "sections": [
                        {
                            "fields": [
                                "namespace",
                                "name",
                                "app",
                                "SUBSYSTEM",
                                "deployment",
                                "deploymentconfig",
                                "deployDate",
                                "distribVersion",
                                "version",
                                "build",
                                "restartPolicy",
                                "imagePullPolicy",
                                "image",
                                "security.istio.io/tlsMode",
                                "jenkinsDeployUser"
                            ],
                            "type": "section",
                            "name": f"k8s-labels-{portal_name}--{cluster['cluster']}",
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
                        },
                        {
                            "name": "pod link",
                            "href": "https://console-openshift-console.apps.%s/k8s/ns/{}/pods/{}" % cluster["cluster"],
                            "label": "Pod link",
                            "icon": "fas fa-external-link-alt",
                            "fields": [
                                "namespace",
                                "name"
                            ]
                        }
                    ],
                    "summary": {
                        "fields": [
                            "namespace",
                            "name",
                            "app",
                            "SUBSYSTEM",
                            # "deployment",
                            "deploymentconfig",
                            "deployDate",
                            "distribVersion",
                            "version",
                            "build",
                            "restartPolicy",
                            "imagePullPolicy",
                            "image",
                            "security.istio.io/tlsMode",
                            "jenkinsDeployUser"
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
                "name": f"k8s-labels-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                "label": cluster["cluster"],
                "description": "k8s labels %s" % cluster["cluster"]
            }

            create_type: dict = cmdb_api("POST", "types/", cmdb_token, data_type_template)
            logger.info(f'Create new label-type with id {create_type["result_id"]}')

            data_cat_template: dict = {
                "public_id": os_portal_category_id["public_id"],
                "name": os_portal_category_id["name"],
                "label": os_portal_category_id["label"],
                "meta": {
                    "icon": "fas fa-folder-open",
                    "order": None
                },
                "parent": os_passports_category_id["public_id"],
                "types": os_portal_category_id["types"]
            }

            if not create_type["result_id"]:
                return

            data_cat_template["types"].append(create_type["result_id"])

            cmdb_api("PUT", "categories/%s" % os_portal_category_id["public_id"], cmdb_token, data_cat_template)
            logger.info(f'Put new label-type id {create_type["result_id"]} in {data_cat_template["name"]}')

            for labels in cluster["labels"]:
                create_label(labels, cmdb_token, create_type["result_id"], user_id)
                logger.info(f'Create label-object {labels["name"]} in {create_type["result_id"]}')
                time.sleep(0.1)

    if not all_objects:
        all_objects: tuple = get_mongodb_objects("framework.objects")

    all_types_labels = tuple(filter(lambda x: "k8s-labels-%s--" % portal_name in x["name"], cmdb_projects))

    for cmdb_cluster in all_types_labels:
        for cluster in all_labels:
            if cmdb_cluster["label"] == cluster["cluster"] and cmdb_cluster["label"]:
                logger.info(f'Update label-objects in {cmdb_cluster["label"]}')
                cmdb_namespaces = tuple(filter(lambda x: x["type_id"] == cmdb_cluster["public_id"], all_objects))

                ex_labels: dict = {
                    label["name"]: label for label in cluster["labels"]
                }

                dg_labels: dict = {
                    pod["fields"][1]["value"]: pod for pod in cmdb_namespaces
                }

                for dg_name, ex_name in zip_longest(set(dg_labels) - set(ex_labels), set(ex_labels) - set(dg_labels)):
                    if not ex_name:
                        logger.info(f'Delete label {dg_labels[dg_name]["fields"][1]["value"]}')
                        cmdb_api("DELETE", "object/%s" % dg_labels[dg_name]["public_id"], cmdb_token)

                    elif not dg_name:
                        create_label(ex_labels[ex_name], cmdb_token, cmdb_cluster["public_id"], user_id)
                        logger.info(f'Create label-object {ex_labels[ex_name]["name"]}')

                    else:
                        template: dict = create_label(ex_labels[ex_name], cmdb_token, cmdb_cluster["public_id"],
                                                      user_id, template=True)
                        payload_object_tmp: dict = {
                            "type_id": dg_labels[dg_name]["type_id"],
                            "status": dg_labels[dg_name]["status"],
                            "version": dg_labels[dg_name]["version"],
                            "creation_time": {
                                "$date": int(time.mktime(dg_labels[dg_name]["creation_time"].timetuple()) * 1000)
                            },
                            "author_id": dg_labels[dg_name]["author_id"],
                            "last_edit_time": {
                                "$date": int(time.time() * 1000)
                            },
                            "editor_id": user_id,
                            "active": dg_labels[dg_name]["active"],
                            "fields": template["fields"],
                            "public_id": dg_labels[dg_name]["public_id"],
                            "views": dg_labels[dg_name]["views"],
                            "comment": ""
                        }

                        create_label(payload_object_tmp, cmdb_token, dg_labels[dg_name]["type_id"], user_id, "PUT")
                        logger.info(
                            f'Update label-object {payload_object_tmp["fields"][1]["value"]} '
                            f'in {dg_labels[dg_name]["type_id"]}'
                        )
