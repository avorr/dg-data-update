#!/usr/local/bin/python3

import time
import json
import requests
from loguru import logger
from datetime import datetime

from env import portal_info
from common_function import dg_api, \
    category_id, \
    get_mongodb_objects


def gtp_app_versions(region: str, auth_info: tuple, all_objects: tuple = ()) -> None:
    """
    Main func for autocomplete labels in DataGerry
    """

    dg_token, user_id = auth_info

    def create_object(version_info: dict, type_id: str, method: str = "POST", template: bool = False) -> dict:

        if method == "PUT":
            return dg_api(method, "object/%s" % version_info["public_id"], dg_token, version_info)

        def get_version(version_info: dict) -> str:
            if next(iter(version_info["version"])) == "ERROR":
                return version_info["version"]["ERROR"]
            if next(iter(version_info["version"])) == "deployment":
                if not version_info["version"]["deployment"]:
                    return "\n".join((version_info["version"]["product-version"],
                                      version_info["version"]["release-version"]))

                return "\n".join(("\n".join(version_info["version"]["deployment"].keys()),
                                  version_info["version"]["product-version"],
                                  version_info["version"]["release-version"]))

            return version_info["version"]

        app_obj: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": user_id,
            "fields": [
                {
                    "name": "name",
                    "value": version_info["service_name"]
                },
                {
                    "name": "vm-name",
                    "value": version_info["name"]
                },
                {
                    "name": "local-ip",
                    "value": version_info["ip"]

                },
                {
                    "name": "tag",
                    "value": version_info["tag"]
                },
                {
                    "name": "version",
                    "value": get_version(version_info)
                },
                {
                    "name": "vm-id",
                    "value": version_info["id"]
                },
                {
                    "name": "record-update-time",
                    "value": datetime.now().strftime("%d.%m.%Y %H:%M")
                }
            ]
        }

        if template:
            return app_obj

        return dg_api("POST", "object/", dg_token, app_obj)

    all_categories: tuple = get_mongodb_objects("framework.categories")

    k8s_category_id = category_id("vm-app-versions", "Vm App Versions", "fas fa-server", dg_token, all_categories)

    k8s_portal_category_id = category_id("app-versions-%s" % region, "App-Versions-%s" % region.upper(),
                                         "far fa-folder-open", dg_token, all_categories, k8s_category_id["public_id"])

    all_app_versions: dict = json.loads(requests.request("GET", portal_info["app_versions"]).content)

    dg_projects: tuple = get_mongodb_objects("framework.types")

    for stand in all_app_versions["info"]:
        if not any(tuple(map(lambda y: y["name"] == f'app-versions-{region}--{stand["project_id"]}', dg_projects))) \
                and stand["modules_version"]:

            payload_type_template: dict = {
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
                        "name": "local-ip",
                        "label": "local ip"
                    },
                    {
                        "type": "text",
                        "name": "tag",
                        "label": "tag"
                    },
                    {
                        "type": "text",
                        "name": "version",
                        "label": "version"
                    },
                    {
                        "type": "text",
                        "name": "vm-id",
                        "label": "vm id"
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
                    "icon": "fab fa-centos",
                    "sections": [
                        {
                            "fields": [
                                "name",
                                "vm-name",
                                "local-ip",
                                "tag",
                                "version",
                                "vm-id",
                                "record-update-time"
                            ],
                            "type": "section",
                            "name": f"app-versions-{region}--{stand['project_id']}",
                            "label": stand["project_id"]
                        }
                    ],
                    "externals": [],
                    "summary": {
                        "fields": [
                            "name",
                            "vm-name",
                            "local-ip",
                            "tag",
                            "version",
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
                "name": f"app-versions-{region}--{stand['project_id']}",
                "label": stand["project_name"],
                "description": stand["desc"]
            }

            create_type = dg_api("POST", "types/", dg_token, payload_type_template)
            logger.info(f'Create new type id {create_type["result_id"]}')

            payload_category: dict = {
                "public_id": k8s_portal_category_id["public_id"],
                "name": k8s_portal_category_id["name"],
                "label": k8s_portal_category_id["label"],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": k8s_category_id["public_id"],
                "types": k8s_portal_category_id["types"]
            }

            if not create_type["result_id"]:
                return

            payload_category["types"].append(create_type["result_id"])

            logger.info(f'Put type {create_type["result_id"]} in category {k8s_portal_category_id["name"]}')
            dg_api("PUT", "categories/%s" % k8s_portal_category_id["public_id"], dg_token, payload_category)

            for version in stand["modules_version"]:
                create_app_version_object = create_object(version, create_type["result_id"])
                logger.info(f"Create new object {create_app_version_object}")

    all_objects: tuple = get_mongodb_objects("framework.objects")

    all_app_types = tuple(filter(lambda x: f"app-versions-%s--" % region in x["name"], dg_projects))

    for app_type in all_app_types:
        for app_versions in all_app_versions["info"]:
            if app_type["name"][len("app-versions-%s--" % region):] == app_versions["project_id"] and \
                    app_versions["modules_version"]:

                dg_app_objects = tuple(filter(lambda x: x["type_id"] == app_type["public_id"], all_objects))

                for app_module in app_versions["modules_version"]:
                    for dg_object in dg_app_objects:
                        app_object: dict = create_object(app_module, app_type["public_id"], template=True)

                        dg_to_diff = dg_object["fields"].copy()
                        tmp_to_diff = app_object["fields"].copy()
                        dg_to_diff.pop(-1)
                        tmp_to_diff.pop(-1)

                        if app_module["id"] == dg_object["fields"][5]["value"] and \
                                app_module["tag"] == dg_object["fields"][3]["value"] and tmp_to_diff != dg_to_diff:
                            update_object_template: dict = {
                                "type_id": dg_object["type_id"],
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
                                "fields": app_object["fields"],
                                "public_id": dg_object["public_id"],
                                "views": dg_object["views"],
                                "comment": ""
                            }
                            create_object(update_object_template, app_type["public_id"], "PUT")
                            logger.info(f'Update app version in {dg_object["type_id"]} type')

                    if f'{app_module["tag"]}--{app_module["id"]}' not in \
                            tuple(map(lambda x: f'{x["fields"][3]["value"]}--{x["fields"][5]["value"]}',
                                      dg_app_objects)):
                        logger.info(f'Create app version in {app_type["public_id"]}')
                        create_object(app_module, app_type["public_id"])

                for dg_object in dg_app_objects:
                    if f'{dg_object["fields"][3]["value"]}--{dg_object["fields"][5]["value"]}' not in \
                            tuple(map(lambda x: f'{x["tag"]}--{x["id"]}', app_versions["modules_version"])):
                        logger.info(
                            f'Delete app version {dg_object["fields"][3]["value"]}--{dg_object["fields"][5]["value"]}'
                        )
                        dg_api("DELETE", "object/%s" % dg_object["public_id"], dg_token)
