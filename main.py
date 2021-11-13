#!/usr/bin/python3

from env import portal_info
from vm_passport import PassportsVM
from os_passport import PassportsOS


if __name__ == '__main__':
    # print(portal_info)

    # all(map(PassportsVM, portal_info))
    all(map(PassportsOS, portal_info))
    # print('!!!!!!!!!!!!!!!'*100)
    # print(f'{cmdb_login[:-1]} + login from jenkins')
    # print(f'{cmdb_password[:-1]} + password from jenkins')
    # print(cmdb_password)