#!/usr/bin/python3

from env import portal_info
from vm_passport import PassportsVM
from os_passport import PassportsOS
from view_settings import visiableSetting

if __name__ == '__main__':
    print(portal_info)
    print('######' * 100)
    # all(map(PassportsVM, portal_info))
    all(map(PassportsOS, portal_info))
    print('os' True)
    if next(iter(portal_info)) == 'PD15':
        print('PD15', True)
        visiableSetting()
