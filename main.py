#!/usr/local/bin/python3

import sys
import subprocess
from loguru import logger

from vm_passport import PassportsVM
from k8s_passport import PassportsK8s
from k8s_labels import LabelsK8s
from app_versions import gtp_app_versions

# from common_function import portal_api
# from view_settings import visible_settings


# from gtp_releases import releases

def main() -> None:
    # all_objects: tuple = PassportsVM(sys.argv[1])
    # PassportsK8s(sys.argv[1], all_objects)
    # PassportsK8s(sys.argv[1])
    # LabelsK8s(sys.argv[1])
    # return

    try:
        all_objects: tuple = PassportsVM(sys.argv[1])
    except EOFError as err:
        logger.error(err)

    try:
        PassportsK8s(sys.argv[1], all_objects)
    except EOFError as err:
        logger.error(err)

    try:
        LabelsK8s(sys.argv[1])
    except EOFError as err:
        logger.error(err)

    try:
        gtp_app_versions(sys.argv[1])
    except EOFError as err:
        logger.error(err)

    # visible_settings()
    subprocess.run(["pkill", "openconnect"])


if __name__ == '__main__':
    main()
