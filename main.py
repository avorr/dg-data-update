#!/usr/bin/python3

import os
import sys
from tools import *
from env import portal_info
from vm_passport import PassportsVM
from os_passport import PassportsOS
from os_labels import LabelsOS
from getObjects import get_dg_objects
from vdcPassports import PassportsVDC
from pprb3Versions import pprb3_versions
from view_settings import visiableSetting
from vm_passport import get_mongodb_objects

# from platformReleases import releases

if __name__ == '__main__':

    # from allObjects import allObjects as all_objects
    # all(map(PassportsOS, portal_info, all_objects))
    # tuple(LabelsOS(foo, all_objects) for foo in portal_info)

    # all_objects = max(map(PassportsVM, portal_info))
    # tuple(PassportsOS(foo, all_objects) for foo in portal_info)
    # tuple(map(LabelsOS, portal_info))
    #
    # if next(iter(portal_info)) == 'PD15':
    #     from view_settings import visiableSetting
    #     visiableSetting()

    # foo = {None: 8383}
    # print(foo.get(next(iter(foo))))

    # if sys.argv[1] == 'PD15':
    #     from view_settings import visiableSetting
    #     visiableSetting()

    # from allProjects import allProjects

    # from vm_passport import get_mongodb_objects
    # dg_types: tuple = get_mongodb_objects('framework.types')
    # get_info_cmdb_vdc = max(filter(lambda y: y['name'] == 'cfc54d92-ca81-4d4f-9e92-b46dd78acaa8', dg_types))
    # print(get_info_cmdb_vdc)

    # if sys.argv[1] == 'PD15':
    #     from view_settings import visiableSetting
    #     visiableSetting()
    # all_objects = PassportsVM(sys.argv[1])
    # from vm_passport import get_mongodb_objects
    # all_objects: tuple = get_mongodb_objects('framework.objects')

    # sys.argv[1] = "PD20"

    # all_types: tuple = get_mongodb_objects('framework.types', {'name': '322b98d0-ae7e-48c6-a64d-6f8cb84042e6'})

    # for i in all_types:
    #     print(i['public_id'])
    # if sys.argv[1] == 'PD15':
    # visiableSetting()
    # exit()
    # pprb3_versions(sys.argv[1])
    # exit()

    if sys.argv[1] == 'PD23':
        try:
            all_objects = PassportsVM(sys.argv[1])
            exit()
        except EOFError as error:
            print(error)

    try:
        all_objects = PassportsVM(sys.argv[1])
    except EOFError as error:
        print(error)

    try:
        PassportsOS(sys.argv[1], all_objects)
    except EOFError as error:
        print(error)

    try:
        LabelsOS(sys.argv[1])
    except EOFError as error:
        print(error)
    # if sys.argv[1] == 'PD15':
    # releases()
    # pprb3_versions(sys.argv[1])
    try:
        visiableSetting()
    except EOFError as error:
        print(error)
