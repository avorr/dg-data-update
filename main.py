#!/usr/local/bin/python3

import sys

from vm_passport import PassportsVM
from k8s_passport import PassportsK8s
from k8s_labels import LabelsK8s
from app_versions import gtp_app_versions

# from common_function import portal_api
# from view_settings import visible_settings


# from gtp_releases import releases

def main() -> None:
    # all_objects: tuple = PassportsVM(sys.argv[1])
    # visible_settings()
    # LabelsK8s(sys.argv[1])
    # return

    try:
        all_objects: tuple = PassportsVM(sys.argv[1])
    except EOFError as error:
        print(error)

    try:
        PassportsK8s(sys.argv[1], all_objects)
    except EOFError as error:
        print(error)

    try:
        LabelsK8s(sys.argv[1])
    except EOFError as error:
        # except:
        #     pass
        print(error)

    try:
        gtp_app_versions(sys.argv[1])
    except EOFError as error:
        print(error)
    # releases()
    # gtp_app_versions(sys.argv[1])

    # visible_settings()


if __name__ == '__main__':
    main()

    # if 0 != 5:
    # raise TypeError("Type not serializable")
    # raise EOFError("asasa")
