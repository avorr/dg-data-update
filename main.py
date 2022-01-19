#!/usr/bin/python3

import sys
from env import portal_info
from vm_passport import PassportsVM
from os_passport import PassportsOS
from os_labels import LabelsOS
# sys.argv = ['', 'PD15']

if __name__ == '__main__':


    from allPprb3Version import allPprb3WfVersions


    for i in allPprb3WfVersions:
        # print(i['pprb3gServers'])
        for ii in i['pprb3gServers']:
            if type(ii['wf_info']) is dict:
                print(ii['wf_info'])
                print(type(ii['wf_info']))

    exit()
    # from allObjects import allObjects
    # from vm_passport import json_read
    # json_read(allObjects[1]['results'][0])

    # all_objects = ()
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

    all_objects = PassportsVM(sys.argv[1])
    PassportsOS(sys.argv[1], all_objects)
    LabelsOS(sys.argv[1])

    if sys.argv[1] == 'PD15':
        from view_settings import visiableSetting
        visiableSetting()