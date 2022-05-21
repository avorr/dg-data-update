#!/usr/bin/python3

import time
import socket
import requests
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

    def create_label(labels_info: dict, cmdb_token: str, type_id: str, author_id: int, method: str = 'POST',
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
            if 'labels' in labels:
                if label in labels:
                    return labels[label]
                elif label in labels['labels']:
                    return labels['labels'][label]
                else:
                    return ''
            else:
                if label in labels:
                    return labels[label]
                else:
                    return ''

        label_object_template: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "namespace",
                    "value": get_label(labels_info, 'namespace')
                },
                {
                    "name": "name",
                    "value": get_label(labels_info, 'name')
                },
                {
                    "name": "app",
                    "value": get_label(labels_info, 'app')
                },
                {
                    "name": "SUBSYSTEM",
                    "value": get_label(labels_info, 'SUBSYSTEM')

                },
                {
                    "name": "deployment",
                    "value": get_label(labels_info, 'deployment')
                },
                {
                    "name": "deploymentconfig",
                    "value": get_label(labels_info, 'deploymentconfig')
                },
                {
                    "name": "deployDate",
                    "value": get_label(labels_info, 'deployDate')
                },
                {
                    "name": "distribVersion",
                    "value": get_label(labels_info, 'distribVersion')
                },
                {
                    "name": "version",
                    "value": get_label(labels_info, 'version')
                },
                {
                    "name": "security.istio.io/tlsMode",
                    "value": get_label(labels_info, 'security.istio.io/tlsMode')
                },
                {
                    "name": "jenkinsDeployUser",
                    "value": get_label(labels_info, 'jenkinsDeployUser')
                }
            ]
        }

        if template:
            return label_object_template

        return cmdb_api("POST", "object/", cmdb_token, label_object_template)

    cmdb_token, user_id = get_dg_token()

    all_categories: tuple = get_mongodb_objects("framework.categories")

    os_passports_category_id: dict = \
        category_id("os-app-labels", "OS App Labels", "fas fa-tags", cmdb_token, all_categories)

    os_portal_category_id: dict = \
        category_id("OS-Labels-%s" % portal_name, "OS-Labels-%s" % portal_name, "fas fa-folder-open", cmdb_token,
                    all_categories, os_passports_category_id['public_id'])

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
            if 'cluster' in info['metric']:
                new_info.append(info)
        return new_info

    cluster_info['data']['result'] = clear_info(cluster_info['data']['result'])
    #### temporary

    clusters = map(lambda x: x["metric"]["cluster"], cluster_info["data"]["result"])

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

        all_labels = list()
        for cluster_name in set(clusters):
            if check_resolves("query-runner.apps.%s" % cluster_name):
                get_labels = requests.request("GET", "https://query-runner.apps.%s/pods" % cluster_name, verify=False)
                if get_labels.status_code == 200:
                    all_labels.append(dict(cluster=cluster_name, labels=json.loads(get_labels.content)))

        return all_labels

    all_labels: list = get_ose_labels(clusters)

    cmdb_projects: tuple = get_mongodb_objects("framework.types")

    for cluster in all_labels:
        if not any(map(lambda y: y['name'] == f"os-labels-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                       cmdb_projects)):

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
                                "security.istio.io/tlsMode",
                                "jenkinsDeployUser"
                            ],
                            "type": "section",
                            "name": f"os-labels-{portal_name}--{cluster['cluster']}",
                            # "name": "os-labels-%s--%s" % (portal_name, cluster['cluster']),
                            "label": cluster['cluster']
                        }
                    ],
                    "externals": [
                        {
                            "name": "cluster link",
                            "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects" %
                                    cluster['cluster'],
                            "label": "Cluster link",
                            "icon": "fas fa-external-link-alt",
                            "fields": []
                        },
                        {
                            "name": "namespace link",
                            "href": "https://console-openshift-console.apps.%s/k8s/cluster/projects/{}" %
                                    cluster['cluster'],
                            "label": "Namespace link",
                            "icon": "fas fa-external-link-alt",
                            "fields": ["namespace"]
                        },
                        {
                            "name": "pod link",
                            "href": "https://console-openshift-console.apps.%s/k8s/ns/{}/pods/{}" % cluster['cluster'],
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
                            "deployment",
                            "deploymentconfig",
                            "deployDate",
                            "distribVersion",
                            "version",
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
                "name": f"os-labels-{portal_name}--{cluster['cluster'].replace('.', '_')}",
                "label": cluster["cluster"],
                "description": "openshift labels %s" % cluster["cluster"]
            }

            create_type: dict = cmdb_api("POST", "types/", cmdb_token, data_type_template)
            print(create_type["result_id"], 'new type id')

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

            put_type_in_category: dict = \
                cmdb_api("PUT", "categories/%s" % os_portal_category_id["public_id"], cmdb_token, data_cat_template)

            print("PUT TYPE IN CATEGORY", put_type_in_category)
            print("DATA CATEGORY TEMPLATE", data_cat_template)

            for labels in cluster["labels"]:
                print(
                    "CREATE OBJECT",
                    create_label(labels, cmdb_token, create_type["result_id"], user_id)
                )
                time.sleep(0.1)

    if not all_objects:
        all_objects: tuple = get_mongodb_objects("framework.objects")

    all_types_labels = tuple(filter(lambda x: "os-labels-%s--" % portal_name in x["name"], cmdb_projects))

    for cmdb_cluster in all_types_labels:
        for cluster in all_labels:
            if cmdb_cluster["label"] == cluster["cluster"] and cmdb_cluster["label"]:
                print(cmdb_cluster["label"], "UPDATE LABELS")
                cmdb_namespaces = tuple(filter(lambda x: x["type_id"] == cmdb_cluster["public_id"], all_objects))

                ex_labels: dict = {
                    label["name"]: label for label in cluster["labels"]
                }

                dg_labels: dict = {
                    pod["fields"][1]["value"]: pod for pod in cmdb_namespaces
                }

                for dg_name, ex_name in zip_longest(set(dg_labels) - set(ex_labels), set(ex_labels) - set(dg_labels)):
                    if not ex_name:
                        print("DELETE LABEL <--->", dg_labels[dg_name])
                        cmdb_api("DELETE", "object/%s" % dg_labels[dg_name]["public_id"], cmdb_token)

                    elif not dg_name:
                        print(
                            "CREATE LABEL <--->", ex_labels[ex_name],
                            create_label(ex_labels[ex_name], cmdb_token, cmdb_cluster["public_id"], user_id)
                        )

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
                        print(
                            create_label(payload_object_tmp, cmdb_token, dg_labels[dg_name]["type_id"], user_id, "PUT")
                        )
