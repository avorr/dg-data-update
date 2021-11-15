#!/usr/bin/python3

from env import portal_info, fortiLogin, fortiPassword
# from vm_passport import PassportsVM
# from os_passport import PassportsOS
# from view_settings import visiableSetting

if __name__ == '__main__':
    print(portal_info)
    print('######' * 100)

    print(fortiLogin[:-1])
    print(fortiLogin[-1:])
    print(fortiPassword[:-1])
    print(fortiPassword[-1:])
    # import time
    # time.sleep(10000000)


    # all(map(PassportsVM, portal_info))
    # all(map(PassportsOS, portal_info))
    # visiableSetting()
