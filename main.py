#!/usr/bin/python3

import sys
from vm_passport import PassportsVM
from os_passport import PassportsOS
from os_labels import LabelsOS
from app_versions import gtp_app_versions
from view_settings import visible_settings


# from gtp_releases import releases

def main() -> None:
    # LabelsOS(sys.argv[1])
    # visible_settings()
    # gtp_app_versions(sys.argv[1])
    # return
    try:
        all_objects: tuple = PassportsVM(sys.argv[1])
    except EOFError as error:
        print(error)

    try:
        PassportsOS(sys.argv[1], all_objects)
    except EOFError as error:
        print(error)

    try:
        LabelsOS(sys.argv[1])
    except EOFError as error:
        # except:
        #     pass
        print(error)

    if sys.argv[1] in ('PD15', 'PD20'):
        gtp_app_versions(sys.argv[1])
    # releases()
    # gtp_app_versions(sys.argv[1])

    visible_settings()


if __name__ == '__main__':
    # main()

    # if 0 != 5:
    # raise TypeError("Type not serializable")
    # raise EOFError("asasa")

    foo = {
        'foo': 'kek',
        'foo1': 'kek2',
        'foo3': [
            1,
            2
        ],
        'foo4': {
          1: '23221',
          2: '23221',
          3: '23221'
        }
    }
    # print(foo.keys())
    match foo.keys():
        case 'foo', 'foo1', 'foo3', 'foo4':
            print(foo)
        case ['foo', 'foo1', 'foo3', 'foo4']:
            print(True)

    d = {0: "zero", 1: "one", 2: "two", 3: "three"}
    match d:
        case {0: "zero1", **remainder}:
            print(remainder)
            # print(remainder)
            pass
        case {0: "zero"}:
            print('2121')
        case {1: "one"}:
            print('#####')





