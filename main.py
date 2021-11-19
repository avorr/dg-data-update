#!/usr/bin/python3

# from env import portal_info
# from vm_passport import PassportsVM
# from os_passport import PassportsOS
# from view_settings import visiableSetting

if __name__ == '__main__':
    from env import fortiLogin, fortiPassword
    print(fortiLogin[:-1])
    print(fortiPassword[:-1])
    exit()

    # print(portal_info)
    # print('######' * 100)
    #
    # all(map(PassportsVM, portal_info))
    # all(map(PassportsOS, portal_info))
    # visiableSetting()
