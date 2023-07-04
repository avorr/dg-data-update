#!/usr/local/bin/python3
import os
from loguru import logger
from common_function import dg_api, get_mongodb_objects, category_id


def passports_stand(region: str, auth_info: tuple) -> None:
    """
    Main func for create vm objects in DataGerry
    :param region: ex: PD15
    :param auth_info
    :return: None
    """
    if get_mongodb_objects("framework.types", {"name": f"passports-{region}"}):
        return

    dg_categories: tuple = get_mongodb_objects("framework.categories")

    dg_token, user_id = auth_info

    passport_stands_id: dict = category_id(
        "passports-stand", "Passports Stand", "fas fa-folder-open", dg_token, dg_categories
    )

    vdc_type_id: int = get_mongodb_objects("framework.types", {"name": f"vdc-{region}"})[0]["public_id"]
    links_k8s_id: int = get_mongodb_objects("framework.types", {"name": f"links-k8s-{region}"})[0]["public_id"]

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
                "type": "textarea",
                "name": "zone",
                "label": "Zone",
                "rows": 30
            },
            {
                "type": "text",
                "name": "git",
                "label": "Git"
            },
            {
                "type": "textarea",
                "name": "postgre-se",
                "label": "Postgre SE",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "kafka-se",
                "label": "Kafka Se",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "audit",
                "label": "Audit",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "iam",
                "label": "IAM",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "pprb",
                "label": "PPRB",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "efs",
                "label": "EFS",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "fd",
                "label": "FD",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "istio",
                "label": "Istio",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "dvp",
                "label": "DVP",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "interactive-documentation",
                "label": "Интерактивная Документация",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "s3",
                "label": "S3",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "jenkins-cd",
                "label": "Jenkins CD",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "sber-works",
                "label": "Инструменты Производственного Процесса",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "journaling",
                "label": "Журналирование",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "monitoring",
                "label": "Мониторинг",
                "rows": 30
            },
            {
                "type": "textarea",
                "name": "k8s",
                "label": "K8s",
                "rows": 30
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
                        "git"
                    ],
                    "type": "section",
                    "name": "passports",
                    "label": "Passports"
                },
                {
                    "fields": [
                        "postgre-se",
                        "kafka-se",
                        "audit",
                        "iam",
                        "pprb",
                        "efs",
                        "fd",
                        "istio",
                        "dvp",
                        "interactive-documentation",
                        "s3",
                        "jenkins-cd",
                        "sber-works",
                        "journaling",
                        "monitoring",
                        "k8s"
                    ],
                    "type": "section",
                    "name": "services",
                    "label": "Services"
                }
            ],
            "externals": [
                {
                    "name": "passport-link",
                    "label": "Passport link",
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
                    "git"
                ]
            }
        },
        "acl": {
            "activated": False,
            "groups": {
                "includes": {}
            }
        },
        "name": f"passports-{region}",
        "label": f"Passports-{region.upper()}",
        "description": f"Passports {region.upper()}"
    }

    create_type: int = dg_api("POST", "types/", dg_token, payload)['result_id']

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

    move_type = dg_api('PUT', "categories/%s" % passport_stands_id['public_id'], dg_token, payload_category)

    logger.info(f"Move type {move_type['result']['public_id']} to category {payload_category['name']}")
