#!/usr/local/bin/python3

import sys
from loguru import logger

from stand_passports import passports_stand
from vm_passports import passports_vm
from k8s_passport import passports_k8s
from k8s_labels import labels_k8s
from app_versions import gtp_app_versions
from common_function import get_dg_token


def main() -> None:
    region: str = sys.argv[1].lower()
    auth_info: tuple = get_dg_token()

    try:
        all_objects: tuple = passports_vm(region, auth_info)
    except EOFError as err:
        logger.error(err)
        all_objects = ()

    try:
        passports_k8s(region, auth_info, all_objects)
    except EOFError as err:
        logger.error(err)

    try:
        labels_k8s(region, auth_info, all_objects)
    except EOFError as err:
        logger.error(err)

    try:
        gtp_app_versions(region, auth_info, all_objects)
    except EOFError as err:
        logger.error(err)

    try:
        passports_stand(region, auth_info)
    except EOFError as err:
        logger.error(err)
    # import subprocess
    # subprocess.run(["pkill", "openconnect"])


def delete_all():
    from common_function import get_mongodb_objects, dg_api, get_dg_token
    dg_token, user_id = get_dg_token()
    dg_categories: tuple = get_mongodb_objects("framework.categories")
    dg_types: tuple = get_mongodb_objects("framework.types")

    # for delete_dg_type in dg_types:
    #     result: dict = dg_api("DELETE", "types/%s" % delete_dg_type["public_id"], dg_token)
    #     logger.info(f'Delete type "{result["raw"]["label"]}" from dg')

    # for delete_category in dg_categories:
    #     result: dict = dg_api("DELETE", "categories/%s" % delete_category["public_id"], dg_token)
    #     logger.info(f'Delete dg category "{result["raw"]["label"]}" from dg')


if __name__ == '__main__':
    main()
