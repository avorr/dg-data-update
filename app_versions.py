#!/usr/local/bin/python3

import time
import requests
from loguru import logger
from datetime import datetime

from tools import *
from env import portal_info
from common_function import cmdb_api
from common_function import category_id
from common_function import get_dg_token
from common_function import get_mongodb_objects


def gtp_app_versions(portal_name: str, all_objects: tuple = ()) -> None:
    """
    Main func for autocomplete labels in DataGerry
    """

    def create_object(version_info: dict, cmdb_token: str, type_id: str, author_id: int, ipa_domain: str, method: str = 'POST',
                      template: bool = False) -> dict:
        if method == 'PUT':
            return cmdb_api(method, "object/%s" % version_info["public_id"], cmdb_token, version_info)

        def get_version(version_info: dict) -> str:
            if next(iter(version_info['version'])) == 'ERROR':
                return version_info['version']['ERROR']
            if next(iter(version_info['version'])) == 'deployment':
                if not version_info['version']['deployment']:
                    return '\n'.join((version_info['version']['product-version'],
                                      version_info['version']['release-version']))

                return '\n'.join(('\n'.join(version_info['version']['deployment'].keys()),
                                  version_info['version']['product-version'],
                                  version_info['version']['release-version']))

            return version_info['version']

            # else:
            #     return None

        app_object_template: dict = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "name",
                    "value": f"{version_info['service_name']}.{ipa_domain}" if ipa_domain else version_info['service_name']
                },
                {
                    "name": "vm-name",
                    "value": version_info['name']
                },
                {
                    "name": "local-ip",
                    "value": version_info['ip']

                },
                {
                    "name": "tag",
                    "value": version_info['tag']
                },
                {
                    "name": "version",
                    "value": get_version(version_info)
                },
                {
                    "name": "vm-id",
                    "value": version_info['id']
                },
                {
                    "name": "record-update-time",
                    "value": datetime.now().strftime('%d.%m.%Y %H:%M')
                }
            ]
        }

        if template:
            return app_object_template

        return cmdb_api("POST", "object/", cmdb_token, app_object_template)

    cmdb_token, user_id = get_dg_token()
    all_categories: tuple = get_mongodb_objects("framework.categories")

    os_passports_category_id = category_id('vm-apps-versions', 'VM Apps Versions',
                                           'fas fa-server', cmdb_token, all_categories)

    os_portal_category_id = \
        category_id("Apps-Version-%s" % portal_name, "Apps-Version-%s" % portal_name, "far fa-folder-open",
                    cmdb_token, all_categories, os_passports_category_id['public_id'])

    all_apps_versions: dict = json.loads(requests.request("GET", portal_info[portal_name]["app_versions"]).content)

    cmdb_projects: tuple = get_mongodb_objects("framework.types")

    for stand in all_apps_versions['info']:
        if not any(tuple(map(lambda y: y['name'] == f"apps-versions-{portal_name}--{stand['project_id']}",
                             cmdb_projects))) and stand['modules_version']:

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
                            "name": f"apps-versions-{portal_name}--{stand['project_id']}",
                            "label": stand['project_id']
                        }
                    ],
                    "externals": [],
                    "summary": {
                        "fields": [
                            "name",
                            "vm-name",
                            "local-ip",
                            "tag",
                            "version"
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
                "name": f"apps-versions-{portal_name}--{stand['project_id']}",
                "label": stand["project_name"],
                # "description": "apps versions %s" % stand["project_id"]
                "description": stand["desc"] if "desc" in stand else ""
            }

            create_type = cmdb_api("POST", "types/", cmdb_token, payload_type_template)
            logger.info(f'Create new type id {create_type["result_id"]}')

            data_cat_template: dict = {
                "public_id": os_portal_category_id['public_id'],
                "name": os_portal_category_id['name'],
                "label": os_portal_category_id['label'],
                "meta": {
                    "icon": "far fa-folder-open",
                    "order": None
                },
                "parent": os_passports_category_id['public_id'],
                "types": os_portal_category_id['types']
            }

            if not create_type['result_id']:
                return

            data_cat_template['types'].append(create_type['result_id'])

            logger.info(f'Put type {create_type["result_id"]} in category {os_portal_category_id["name"]}')
            cmdb_api('PUT', "categories/%s" % os_portal_category_id['public_id'], cmdb_token, data_cat_template)

            for version in stand['modules_version']:
                create_app_version_object = create_object(version, cmdb_token, create_type['result_id'],
                                                          user_id, stand["desc"])
                logger.info(f'Create new object {create_app_version_object}')
                time.sleep(0.1)

    all_objects: tuple = get_mongodb_objects("framework.objects")

    all_app_types = tuple(filter(lambda x: f'apps-versions-%s--' % portal_name in x['name'], cmdb_projects))

    for app_type in all_app_types:
        for apps_versions in all_apps_versions["info"]:
            if app_type['name'][len("apps-versions-%s--" % portal_name):] == apps_versions['project_id'] and apps_versions["modules_version"]:

                dg_apps_objects = tuple(filter(lambda x: x['type_id'] == app_type['public_id'], all_objects))

                for app_module in apps_versions['modules_version']:
                    for dg_object in dg_apps_objects:
                        app_object_template: dict = create_object(app_module, cmdb_token, app_type['public_id'],
                                                                  user_id, app_type["description"], template=True)
                        if app_module['id'] == dg_object['fields'][5]['value'] and \
                                app_module['tag'] == dg_object['fields'][3]['value'] and \
                                app_object_template['fields'] != dg_object['fields']:
                            update_object_template: dict = {
                                "type_id": dg_object['type_id'],
                                "status": dg_object['status'],
                                "version": dg_object['version'],
                                "creation_time": {
                                    "$date": int(time.mktime(dg_object['creation_time'].timetuple()) * 1000)
                                },
                                "author_id": dg_object['author_id'],
                                "last_edit_time": {
                                    "$date": int(time.time() * 1000)
                                },
                                "editor_id": user_id,
                                "active": dg_object["active"],
                                "fields": app_object_template['fields'],
                                "public_id": dg_object['public_id'],
                                "views": dg_object["views"],
                                "comment": ""
                            }
                            create_object(update_object_template, cmdb_token, app_type['public_id'],
                                          user_id, app_type["description"], 'PUT')
                            logger.info(f'Update app version in {dg_object["type_id"]} type')

                    if f'{app_module["tag"]}--{app_module["id"]}' not in \
                            tuple(map(lambda x: f'{x["fields"][3]["value"]}--{x["fields"][5]["value"]}',
                                      dg_apps_objects)):
                        logger.info(f'Create app version in {app_type["public_id"]}')
                        create_object(app_module, cmdb_token, app_type['public_id'], user_id, app_type["description"])
                        time.sleep(0.1)

                for dg_object in dg_apps_objects:
                    if f'{dg_object["fields"][3]["value"]}--{dg_object["fields"][5]["value"]}' not in \
                            tuple(map(lambda x: f'{x["tag"]}--{x["id"]}', apps_versions['modules_version'])):
                        logger.info(
                            f'Delete app version {dg_object["fields"][3]["value"]}--{dg_object["fields"][5]["value"]}'
                        )
                        cmdb_api("DELETE", "object/%s" % dg_object['public_id'], cmdb_token)
                        time.sleep(0.1)


if __name__ == '__main__':
    gtp_app_versions(next(iter(portal_info)))
