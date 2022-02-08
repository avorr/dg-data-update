#!/usr/bin/python3
import os
import sys
from env import portal_info
from vm_passport import PassportsVM
from os_passport import PassportsOS
from os_labels import LabelsOS
from getObjects import get_dg_objects
from vdcPassports import PassportsVDC
from pprb3Versions import pprb3Versions
from view_settings import visiableSetting

if __name__ == '__main__':
    # from allPprb3Version import allPprb3WfVersions
    # for i in allPprb3WfVersions:
    # print(i['pprb3gServers'])
    # for ii in i['pprb3gServers']:
    #     if type(ii['wf_info']) is dict:
    #         print(ii['wf_info'])
    #         print(type(ii['wf_info']))
    # exit()

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

    # foo = range(1, 11)
    # bar = range(11, 21)
    #
    # zip = dict()
    # for i in foo:
    #     for y in bar:
    #         zip[i] = y

    # print(zip)
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
    # exit()

    # for project in allProjects:
    #     if not any(map(lambda x: x['name'] == allProjects[project]['id'], dg_types)):
    #         print(project)

    # def get_metric(ns_info: list, looking_metric: str, type_metric: str) -> str:
    #     for metric in ns_info:
    #         if metric[0] == looking_metric and metric[1] == type_metric:
    #             return metric[2][1]
    #         else:
    #             return 0


    # get_usage = lambda x, y: "%.2f" % ((float(x) / float(y)) * 100) if float(y) != 0.0 else str(float(y))
    #
    # vm_info = {'namespace': 'gt-sol-dev-entrance-01',
    #            'info': [('limits.cpu', 'hard', [1644362032, '16']), ('requests.cpu', 'used', [1644362032, '3']),
    #                     ('requests.memory', 'used', [1644362032, '12301893632'])]}

    # print(get_metric(vm_info['info'], 'limits.cpu', 'used'))
    # print(get_metric(vm_info['info'], 'limits.cpu', 'hard'))
    #
    # print(get_usage(get_metric(vm_info['info'], 'limits.cpu', 'used'), get_metric(vm_info['info'], 'limits.cpu', 'hard')))

    # exit()

    # get_dg_objects()
    # PassportsVDC(sys.argv[1])

    # if sys.argv[1] == 'PD15':
    #     from view_settings import visiableSetting
    #     visiableSetting()
    # all_objects = PassportsVM(sys.argv[1])
    # from vm_passport import get_mongodb_objects
    # all_objects: tuple = get_mongodb_objects('framework.objects')


    all_objects = PassportsVM(sys.argv[1])
    PassportsOS(sys.argv[1], all_objects)
    # exit()
    LabelsOS(sys.argv[1])
    pprb3Versions(sys.argv[1])
    visiableSetting()

    # if sys.argv[1] == 'PD15':
    #     from view_settings import visiableSetting
    #     visiableSetting()
