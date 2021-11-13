#!/usr/bin/python3

from env import portal_info, cmdb_login, cmdb_password
from vm_passport import PassportsVM
from os_passport import PassportsOS


if __name__ == '__main__':
    print(portal_info)

    # print(tuple(map(PassportsVM, portal_info)))
    # all(map(PassportsOS, portal_info))
    print('!!!!!!!!!!!!!!!'*100)
    print(cmdb_login)
    print(cmdb_password)