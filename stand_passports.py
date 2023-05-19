#!/usr/local/bin/python3
import os
from loguru import logger
from common_function import cmdb_api, \
    get_mongodb_objects, \
    category_id


def passport_stands(region: str, auth_info: tuple):
    """
    Main func for create vm objects in DataGerry
    :param region: ex: PD15
    :param auth_info
    :return: tuple | None
    """

    dg_token, user_id = auth_info

    exist_passports: tuple = get_mongodb_objects("framework.types", {"name": f"passports-{region.lower()}"})

    if exist_passports:
        return

    dg_categories: tuple = get_mongodb_objects("framework.categories")

    passport_stands_id: dict = category_id(
        "passport-stands", "Passport Stands", "fas fa-folder-open", dg_token, dg_categories
    )

    vdc_type_id: int = get_mongodb_objects("framework.types", {"name": f"vdc-{region.lower()}"})[0]["public_id"]
    links_k8s_id: int = get_mongodb_objects("framework.types", {"name": f"links-k8s-{region.lower()}"})[0]["public_id"]

    payload: dict = {
        "fields": [
            {
                "type": "text",
                "name": "name",
                "label": "Name"
            },
            {
                "type": "ref",
                "name": "passport-vdc",
                "label": "Passport-Vdc",
                "ref_types": [
                    vdc_type_id
                ],
                "summaries": [],
            },
            {
                "type": "ref",
                "name": "passport-k8s",
                "label": "Passport-K8s",
                "ref_types": [
                    links_k8s_id
                ],
                "summaries": [],
            },
            {
                "type": "text",
                "name": "bitwarden",
                "label": "Bitwarden"
            },
            {
                "type": "text",
                "name": "zone",
                "label": "Zone"
            },
            {
                "type": "text",
                "name": "git",
                "label": "Git"
            },
            {
                "type": "text",
                "name": "portal",
                "label": "Portal"
            }
        ],
        "active": True,
        "version": "1.0.0",
        "author_id": user_id,
        "render_meta": {
            "icon": "fa fa-cube",
            "sections": [
                {
                    "fields": [
                        "name",
                        "passport-vdc",
                        "passport-k8s",
                        "bitwarden",
                        "zone",
                        "git",
                        "portal"
                    ],
                    "type": "section",
                    "name": "passports",
                    "label": "Passports"
                }
            ],
            "externals": [
                {
                    "name": "link",
                    "label": "Link",
                    "icon": "fas fa-external-link-alt",
                    "href": "%s?id={}" % os.getenv("PASSPORTS_URL"),
                    "fields": [
                        "object_id"
                    ]
                }
            ],
            "summary": {
                "fields": [
                    "name",
                    "passport-vdc",
                    "passport-k8s",
                    "bitwarden",
                    "zone",
                    "git",
                    "portal"
                ]
            }
        },
        "acl": {
            "activated": False,
            "groups": {
                "includes": {}
            }
        },
        "name": f"passports-{region.lower()}",
        "label": f"Passports-{region}",
        "description": f"Passports {region}"
    }

    create_type: int = cmdb_api("POST", "types/", dg_token, payload)['result_id']

    if not create_type:
        return None

    logger.info(f"Create new type with id -> {create_type}")

    payload_category: dict = {
        "public_id": passport_stands_id['public_id'],
        "name": passport_stands_id['name'],
        "label": passport_stands_id['label'],
        "meta": {
            "icon": "fas fa-folder-open",
            "order": None
        },
        # "parent": portal_stands_id["public_id"],
        "types": passport_stands_id['types']
    }

    payload_category['types'].append(create_type)

    move_type = cmdb_api('PUT', "categories/%s" % passport_stands_id['public_id'], dg_token, payload_category)

    logger.info(f"Move type {move_type['result']['public_id']} to category {payload_category['name']}")
