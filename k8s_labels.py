#!/usr/local/bin/python3

import time
import json
import socket
import requests
from loguru import logger
from itertools import zip_longest
from collections import defaultdict
from datetime import datetime

from env import portal_info
from common_function import get_mongodb_objects, category_id, dg_api, get_k8s_info


def labels_k8s(region: str, auth_info: tuple, all_objects: tuple = ()) -> None:
    """
    main func for autocomplete labels in DataGerry
    :param region:
    :param auth_info:
    :param all_objects:
    :return:
    """
    if portal_info["metrics"] == "false":
        return

    dg_token, user_id = auth_info

    def create_label(labels_info: dict, type_id: str, method: str = "POST", template: bool = False) -> dict:
        """
        func to create or update or delete label objects in DataGerry CMDB
        :param labels_info:
        :param type_id:
        :param method:
        :param template:
        :return:
        """

        if method == "PUT":
            return dg_api(method, "object/%s" % labels_info["public_id"], dg_token, labels_info)

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

        def get_resources(labels: dict, metric_type: str, label: str) -> str:
            """
            Func to get labels from ose exporter
            :param labels:
            :param metric_type:
            :param label:
            :return:
            """
            if "resources" in labels:
                return defaultdict(str, labels["resources"][metric_type])[label]
            return ""

        label_object_template: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": user_id,
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
                    "name": "subsystem",
                    "value": get_label(labels_info, "SUBSYSTEM")

                },
                {
                    "name": "deployment",
                    "value": get_label(labels_info, "deployment")
                },
                {
                    "name": "deployment-config",
                    "value": get_label(labels_info, "deploymentconfig")
                },
                {
                    "name": "deploy-date",
                    "value": get_label(labels_info, "deployDate")
                },
                {
                    "name": "distrib-version",
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
                    "name": "limits-cpu",
                    "value": get_resources(labels_info, "limits", "cpu")
                },
                {
                    "name": "limits-ram",
                    "value": get_resources(labels_info, "limits", "memory")
                },
                {
                    "name": "requests-cpu",
                    "value": get_resources(labels_info, "requests", "cpu")
                },
                {
                    "name": "requests-ram",
                    "value": get_resources(labels_info, "requests", "memory")
                },
                {
                    "name": "log-level",
                    "value": get_label(labels_info, "logLevel")
                },
                {
                    "name": "restart-policy",
                    "value": get_label(labels_info, "restartPolicy")
                },
                {
                    "name": "image-pull-policy",
                    "value": get_label(labels_info, "imagePullPolicy")
                },
                {
                    "name": "image",
                    "value": get_label(labels_info, "image")
                },
                {
                    "name": "security-istio-io-tls-mode",
                    "value": get_label(labels_info, "security.istio.io/tlsMode")
                },
                {
                    "name": "jenkins-deploy-user",
                    "value": get_label(labels_info, "jenkinsDeployUser")
                },
                {
                    "name": "record-update-time",
                    "value": datetime.now().strftime('%d.%m.%Y %H:%M')
                }
            ]
        }

        if template:
            return label_object_template

        return dg_api("POST", "object/", dg_token, label_object_template)

    all_categories: tuple = get_mongodb_objects("framework.categories")

    k8s_passports_category_id: dict = category_id("k8s-app-labels", "K8s App Labels", "fas fa-tags", dg_token,
                                                  all_categories)

    k8s_portal_category_id: dict = category_id(f"k8s-labels-{region}", f"K8s-Labels-{region.upper()}",
                                               "fas fa-folder-open", dg_token, all_categories,
                                               k8s_passports_category_id["public_id"])

    # def get_k8s_info() -> list:
    #     """
    #     Func to get json from ose exporter
    #     :return:
    #     """
    #     info = list()
    #     for metrics_url in portal_info["metrics"].split(";"):
    #         info.append(json.loads(requests.request("GET", metrics_url.strip(), timeout=3).content)['data']['result'])
    #
    #     # return json.loads(requests.request("GET", portal_info["metrics"]).content)
    #     return info

    clusters_info: list = get_k8s_info()

    clusters_name = set([cluster['metric']['cluster'] for cluster in clusters_info])

    def get_k8s_labels(clusters: set) -> list:
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
                logger.error(dns_name, Error)
                return False

        def check_port(checked_host: str, port: int) -> bool:
            """
            function to check server's port availability
            :param checked_host:
            :param port:
            :return: bool
            """
            if not checked_host:
                return False
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                return s.connect_ex((checked_host, port)) == 0

        all_labels = list()
        for k8s_name in clusters:
            if check_resolves(f"query-runner.apps.{k8s_name}") and check_port(f"query-runner.apps.{k8s_name}", 443):
                get_labels = requests.request("GET", f"https://query-runner.apps.{k8s_name}/pods", verify=False)
                if get_labels.status_code == 200:
                    all_labels.append(dict(cluster=k8s_name, labels=json.loads(get_labels.content)))

        return all_labels

    all_labels: list = get_k8s_labels(clusters_name)

    dg_projects: tuple = get_mongodb_objects("framework.types")

    for cluster in all_labels:
        search_cluster = False
        for dg_project in dg_projects:
            if dg_project['name'] == f'k8s-labels-{region}--{cluster["cluster"].replace(".", "_")}':
                search_cluster = True
                break

        if not search_cluster:

            # if not any(tuple(map(lambda y: y["name"] == f'k8s-labels-{region}--{cluster["cluster"].replace(".", "_")}',
            #                      dg_projects))):

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
                        "name": "subsystem",
                        "label": "SUBSYSTEM"
                    },
                    {
                        "type": "text",
                        "name": "deployment",
                        "label": "deployment"
                    },
                    {
                        "type": "text",
                        "name": "deployment-config",
                        "label": "deploymentconfig"
                    },
                    {
                        "type": "text",
                        "name": "deploy-date",
                        "label": "deployDate"
                    },
                    {
                        "type": "text",
                        "name": "distrib-version",
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
                        "name": "limits-cpu",
                        "label": "limits cpu"
                    },
                    {
                        "type": "text",
                        "name": "limits-ram",
                        "label": "limits ram"
                    },
                    {
                        "type": "text",
                        "name": "requests-cpu",
                        "label": "requests cpu"
                    },
                    {
                        "type": "text",
                        "name": "requests-ram",
                        "label": "requests ram"
                    },
                    {
                        "type": "text",
                        "name": "log-level",
                        "label": "log level"
                    },
                    {
                        "type": "text",
                        "name": "restart-policy",
                        "label": "restartPolicy"
                    },
                    {
                        "type": "text",
                        "name": "image-pull-policy",
                        "label": "imagePullPolicy"
                    },
                    {
                        "type": "text",
                        "name": "image",
                        "label": "image"
                    },
                    {
                        "type": "text",
                        "name": "security-istio-io-tls-mode",
                        "label": "security.istio.io/tlsMode"
                    },
                    {
                        "type": "text",
                        "name": "jenkins-deploy-user",
                        "label": "jenkinsDeployUser"
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
                    "icon": "fas fa-dharmachakra",
                    "sections": [
                        {
                            "fields": [
                                "namespace",
                                "name",
                                "app",
                                "subsystem",
                                "deployment",
                                "deployment-config",
                                "deploy-date",
                                "distrib-version",
                                "version",
                                "build",
                                "limits-cpu",
                                "limits-ram",
                                "requests-cpu",
                                "requests-ram",
                                "log-level",
                                "restart-policy",
                                "image-pull-policy",
                                "image",
                                "security-istio-io-tls-mode",
                                "jenkins-deploy-user",
                                "record-update-time"
                            ],
                            "type": "section",
                            "name": f"k8s-labels-{region}--{cluster['cluster']}",
                            "label": cluster["cluster"]
                        }
                    ],
                    "externals": [],
                    # "externals": [
                    #     {
                    #         "name": "cluster-link",
                    #         "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects" %
                    #                 cluster["cluster"],
                    #         "label": "Cluster link",
                    #         "icon": "fas fa-external-link-alt",
                    #         "fields": []
                    #     },
                    #     {
                    #         "name": "namespace-link",
                    #         "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects/{}" %
                    #                 cluster["cluster"],
                    #         "label": "Namespace link",
                    #         "icon": "fas fa-external-link-alt",
                    #         "fields": ["namespace"]
                    #     },
                    #     {
                    #         "name": "pod-link",
                    #         "href": "https://console-openshift-console.apps.%s/k8s/ns/{}/pods/{}" % cluster[
                    #             "cluster"],
                    #         "label": "Pod link",
                    #         "icon": "fas fa-external-link-alt",
                    #         "fields": [
                    #             "namespace",
                    #             "name"
                    #         ]
                    #     }
                    # ],
                    "summary": {
                        "fields": [
                            "namespace",
                            "name",
                            "app",
                            "subsystem",
                            # "deployment",
                            "deployment-config",
                            "deploy-date",
                            "distrib-version",
                            "version",
                            "build",
                            "limits-cpu",
                            "limits-ram",
                            "requests-cpu",
                            "requests-ram",
                            "log-level",
                            "restart-policy",
                            "image-pull-policy",
                            "image",
                            "security-istio-io-tls-mode",
                            "jenkins-deploy-user",
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
                "name": f"k8s-labels-{region}--{cluster['cluster'].replace('.', '_')}",
                "label": cluster["cluster"],
                "description": "K8s Labels %s" % cluster["cluster"]
            }

            create_type: dict = dg_api("POST", "types/", dg_token, data_type_template)
            logger.info(f'Create new label-type with id {create_type["result_id"]}')

            data_category_tmp: dict = {
                "public_id": k8s_portal_category_id["public_id"],
                "name": k8s_portal_category_id["name"],
                "label": k8s_portal_category_id["label"],
                "meta": {
                    "icon": "fas fa-folder-open",
                    "order": None
                },
                "parent": k8s_passports_category_id["public_id"],
                "types": k8s_portal_category_id["types"]
            }

            if not create_type["result_id"]:
                return

            data_category_tmp["types"].append(create_type["result_id"])

            dg_api("PUT", "categories/%s" % k8s_portal_category_id["public_id"], dg_token, data_category_tmp)
            logger.info(f'Put new label-type id {create_type["result_id"]} in {data_category_tmp["name"]}')

            for labels in cluster["labels"]:
                create_label(labels, create_type["result_id"])
                logger.info(f'Create label-object {labels["name"]} in {create_type["result_id"]}')

    if not all_objects:
        all_objects: tuple = get_mongodb_objects("framework.objects")

    all_types_labels = tuple(filter(lambda x: "k8s-labels-%s--" % region in x["name"], dg_projects))

    for dg_cluster in all_types_labels:
        if dg_cluster['label'] not in clusters_name:
            logger.info(f"Delete k8s labels cluster {dg_cluster['label']} type from DG")
            dg_api("DELETE", "types/%s" % dg_cluster["public_id"], dg_token)
        for cluster in all_labels:
            if dg_cluster["label"] == cluster["cluster"] and dg_cluster["label"]:
                logger.info(f'Update label-objects in {dg_cluster["label"]}')
                dg_namespaces = tuple(filter(lambda x: x["type_id"] == dg_cluster["public_id"], all_objects))

                ex_labels: dict = {
                    label["name"]: label for label in cluster["labels"]
                }

                dg_labels: dict = {
                    pod["fields"][1]["value"]: pod for pod in dg_namespaces
                }

                for dg_name, ex_name in zip_longest(set(dg_labels) - set(ex_labels), set(ex_labels) - set(dg_labels)):
                    if not ex_name:
                        logger.info(f'Delete label {dg_labels[dg_name]["fields"][1]["value"]}')
                        dg_api("DELETE", "object/%s" % dg_labels[dg_name]["public_id"], dg_token)

                    elif not dg_name:
                        logger.info(f'Create label-object {ex_labels[ex_name]["name"]}')
                        create_label(ex_labels[ex_name], dg_cluster["public_id"])

                    else:
                        template: dict = create_label(ex_labels[ex_name], dg_cluster["public_id"], template=True)
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

                        create_label(payload_object_tmp, dg_labels[dg_name]["type_id"], "PUT")
                        logger.info(
                            f'Update label-object {payload_object_tmp["fields"][1]["value"]} '
                            f'in {dg_labels[dg_name]["type_id"]}'
                        )
