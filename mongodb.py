# import pymongo

import requests
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import json
from pymongo import MongoClient


from bson.objectid import ObjectId

def json_read(json_object: dict):
    print(json.dumps(json_object, indent=4))



def cmdb_api(method: str, api_method: str = '', token: str = '', payload: dict = '') -> dict:
    cmdb_api_url: str = "https://cmdb.common.gos-tech.xyz/rest/"
    headers_cmdb_api: dict = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token
    }
    return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                       data=json.dumps(payload)).content)


def get_cmdb_token() -> str:
    auth_payload: dict = {
        "user_name": cmdb_login,
        "password": cmdb_password
    }
    # check_cmdb_auth = cmdb_api('GET', 'users/')
    # print(check_cmdb_auth)
    user_info = cmdb_api('POST', 'auth/login', payload=auth_payload)
    return user_info['token'], user_info['user']['public_id']


cmdb_token, id_user = get_cmdb_token()

number_of_tread = lambda x: int(x) if x < 10 and x != 0 else int((x + 1) ** 0.7)


def get_info_from_all_page(cmdb_item: str) -> tuple:
    numbers_of_pages = cmdb_api('GET', f"{cmdb_item}/", cmdb_token)['pager']['total_pages']

    def get_info_from_one_page(page_number: int):
        return cmdb_api('GET', f'{cmdb_item}/?page={page_number}', cmdb_token)

    full_info = list()
    with ThreadPoolExecutor(max_workers=number_of_tread(numbers_of_pages)) as executor:
        for page_info in executor.map(get_info_from_one_page, range(1, numbers_of_pages + 1)):
            full_info.append(page_info)
    return tuple(full_info)


cmdb_projects = get_info_from_all_page('types')
cmdb_projects_vm, cmdb_projects_os = list(), list()
for item in cmdb_projects:
    for type in item['results']:
        if type['render_meta']['sections'][0]['fields'][0] == 'name':
            cmdb_projects_vm.append(type['public_id'])
        elif type['render_meta']['sections'][0]['fields'][0] == 'namespace':
            cmdb_projects_os.append(type['public_id'])

cmdb_users = (17,)
# print(cmdb_projects_vm)
# print(cmdb_projects_os)

connection_sring = 'mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb'
cluster = MongoClient(connection_sring)

db = cluster['cmdb']

# users_settings = max(filter(lambda x: x['name'] == 'management.users.settings', collection))
for user_id in cmdb_users:
    users_settings = db.get_collection('management.users.settings')
    visibleSettings = users_settings.find({'user_id': user_id})

    default_setting = {
        "_id": "6187035f74b824c96a0a9af7",
        "setting_type": "APPLICATION",
        "resource": "framework-object-type-1009",
        "user_id": 17,
        "payloads": [
            {
                "id": "table-objects-type",
                "tableStates": []
            }
        ]
    }

    default_setting2 = {'_id': ObjectId('6187035f74b824c96a0a9af7'), 'setting_type': 'APPLICATION', 'resource': 'framework-object-type-1009', 'user_id': 17, 'payloads': [{'id': 'table-objects-type', 'tableStates': []}]}
    default_setting3 = {'_id': ObjectId('6187035f74b824c96a0a9af7'), 'setting_type': 'APPLICATION', 'resource': 'framework-object-type-1009', 'user_id': 17, 'payloads': [{'id': 'table-objects-type', 'tableStates': [], 'currentState': {'name': '', 'page': 1, 'pageSize': 50, 'sort': {'name': 'public_id', 'order': -1}, 'visibleColumns': ['fields.namespace', 'fields.limits.cpu-hard', 'fields.limits.cpu-used', 'fields.cores-usage', 'fields.limits.memory-hard', 'fields.limits.memory-used', 'fields.memory-usage', 'actions']}}]}

    default_setting4 = {
        "_id": "6187035f74b824c96a0a9af7",
        "setting_type": "APPLICATION",
        "resource": "framework-object-type-1009",
        "user_id": 17,
        "payloads": [
            {
                "id": "table-objects-type",
                "tableStates": [],
                "currentState": {
                    "name": "",
                    "page": 1,
                    "pageSize": 50,
                    "sort": {
                        "name": "public_id",
                        "order": -1
                    },
                    "visibleColumns": [
                        "fields.namespace",
                        "fields.limits.cpu-hard",
                        "fields.limits.cpu-used",
                        "fields.cores-usage",
                        "fields.limits.memory-hard",
                        "fields.limits.memory-used",
                        "fields.memory-usage",
                        "actions"
                    ]
                }
            }
        ]
    }
    del default_setting4['_id']






    visibleColumnsVm = [
        "fields.name",
        "fields.vm-name",
        "fields.os-type",
        "fields.flavor",
        "fields.cpu",
        "fields.ram",
        "fields.disk",
        "fields.additional-disk",
        "fields.local-ip",
        "fields.public-ip",
        "fields.state",
        "fields.creation-date"
    ]

    payloads_vm = {
        "id": "table-objects-type",
        "tableStates": [],
        "currentState": {
            "name": "",
            "page": 1,
            "pageSize": 200,
            "sort": {
                "name": "public_id",
                "order": -1
            },
            "visibleColumns": [
                "fields.name",
                "fields.vm-name",
                "fields.os-type",
                "fields.flavor",
                "fields.cpu",
                "fields.ram",
                "fields.disk",
                "fields.additional-disk",
                "fields.local-ip",
                "fields.public-ip",
                "fields.state",
                "fields.creation-date"
            ]
        }
    }

    # json_read(bar)
    # foo = '                             dadas          '
    # print(foo.strip(), 'dsdsds')
    # print(foo, 'dsdsds')
    # exit()
    # print(tuple(filter(lambda x: 'framework-object-type-' in x['resource'], visibleSettings)))
    # if 'framework-object-type-1012' in map(lambda x: x['resource'], visibleSettings):
    #     print(True)

    # print(existVisibleSettings)
    # if 'framework-object-type-1012' in existVisibleSettings:
    #     print(True)
    # exit()
    # print(visibleSettings)
        # if f'framework-object-type-{cmdb_type}' in existVisibleSettings:
    for cmdb_type in cmdb_projects_os:
        # print(cmdb_type)

        # for settings in visibleSettings:
        #     print(settings)
        # for i in visibleSettings:
        #     if '1012' in i['resource']:
        #         print(i['resource'])
        print(visibleSettings)
        exit()
        for settings in visibleSettings:
            # if f'framework-object-type-{cmdb_type}' in existVisibleSettings:
            print(settings['resource'])
            if f'framework-object-type-{cmdb_type}' == settings['resource']:
                # print(tuple(map(lambda x: x['resource'], visibleSettings)))
                print('IN', cmdb_type)
                # for settings in visibleSettings:
                if 'currentState' in settings['payloads'][0]:
                    settings['_id'] = str(settings['_id'])
                        # json_read(settings)
                        # exit()
                    if 'fields.name' in settings['payloads'][0]['currentState']["visibleColumns"]:
                        if (set(settings['payloads'][0]['currentState']["visibleColumns"]) - set(visibleColumnsVm)) or \
                                settings['payloads'][0]['currentState']['pageSize'] != 200:
                            # print(set(settings['payloads'][0]['currentState']["visibleColumns"]) - set(visibleColumns))
                            settings['payloads'][0]['currentState']['pageSize'] = 200
                            settings['payloads'][0]['currentState']["visibleColumns"] = visibleColumnsVm

                            # update_view_settings = users_settings.update_one({"_id": settings['_id']}, {"$set": settings})
                            # print(update_view_settings.raw_result)
                    elif 'namespace' in settings['payloads'][0]['currentState']["visibleColumns"]:
                        print(settings)
                else:
                    # settings['_id'] = str(settings['_id'])
                    print(settings)
                    # json_read(settings)
                    # exit()
                    # print(settings)

        exit()
        existVisibleSettings = tuple((map(lambda x: x['resource'], visibleSettings)))

        if f'framework-object-type-{cmdb_type}' not in existVisibleSettings and cmdb_type == 1013:
            print('framework-object-type-1012' == f'framework-object-type-{cmdb_type}')

            print('NOT IN', cmdb_type)
            print(f'framework-object-type-{cmdb_type}')
            default_setting4['resource'] = f"framework-object-type-{cmdb_type}"
            default_setting4['user_id'] = user_id
            # json_read(default_setting4)
            # create_view_settings = users_settings.insert_one(default_setting4)
            # print(create_view_settings)



                # if int(settings['resource'].replace('framework-object-type-', '')) not in cmdb_projects_vm or int(settings['resource'].replace('framework-object-type-', '')) not in cmdb_projects_os:


                # if int(settings['resource'].replace('framework-object-type-', '')) not in cmdb_projects_os:
                #    # create_view_settings = users_settings.insert_one({"_id": settings['_id']}, {"$set": settings})
                #     settings['_id'] = str(settings['_id'])
                #     print(settings)
                #     print(cmdb_type)
                    # json_read(settings)

    exit()
    '''
        for cmdb_type in cmdb_projects_vm:
            # if cmdb_type == 925:
            # if '925' in settings['resource'] or '868' in settings['resource']:
            if settings['resource'] != f'framework-object-type-{cmdb_type}':
                if 'currentState' in settings['payloads'][0]:
                    settings['_id'] = str(settings['_id'])
                    # json_read(settings)
                # exit()
                    if 'fields.name' in settings['payloads'][0]['currentState']["visibleColumns"]:
                        if (set(settings['payloads'][0]['currentState']["visibleColumns"]) - set(visibleColumnsVm)) or \
                                settings['payloads'][0]['currentState']['pageSize'] != 200:
                            # print(set(settings['payloads'][0]['currentState']["visibleColumns"]) - set(visibleColumns))
                            settings['payloads'][0]['currentState']['pageSize'] = 200
                            settings['payloads'][0]['currentState']["visibleColumns"] = visibleColumnsVm
    
                            # update_view_settings = users_settings.update_one({"_id": settings['_id']}, {"$set": settings})
                            # print(update_view_settings.raw_result)
                    elif 'namespace' in settings['payloads'][0]['currentState']["visibleColumns"]:
                        print(settings)
                else:
    
                    settings['_id'] = str(settings['_id'])
                    print(settings)
                    # json_read(settings)
                    # exit()
                    # print(settings)
    '''
    # json_read(settings['payloads'][0]['currentState']["visibleColumns"])
    # print(settings['payloads'][0]['currentState']["visibleColumns"].index('active'))
    # if 'active' in settings['payloads'][0]['currentState']["visibleColumns"]:
    #     print(True)

    # users_settings.update_one({"_id": i['_id']}, {"$set": i})

    # print(db.get_collection('management.users.settings'))

    # for i in collection:
    #     print(i)
    # db = cluster.cmdb

    # print(db)

    '''
    {
        _id: ObjectId('61841880d9267a64e60a9a88'),
        setting_type: 'APPLICATION',
        resource: 'framework-object-type-868',
        user_id: 17,
        payloads: [
            {
                id: 'table-objects-type',
                tableStates: [],
                currentState: {
                    name: '',
                    page: 1,
                    pageSize: 50,
                    sort: {
                        name: 'public_id',
                        order: -1
                    },
                    visibleColumns: [
                        'active',
                        'public_id',
                        'fields.name',
                        'fields.vm-name',
                        'fields.os-type',
                        'fields.flavor',
                        'fields.cpu',
                        'fields.ram',
                        'fields.disk',
                        'fields.additional-disk',
                        'fields.local-ip',
                        'fields.public-ip',
                        'fields.state',
                        'fields.creation-date',
                        'author_id',
                        'creation_time',
                        'last_edit_time',
                        'actions'
                    ]
                }
            }
        ]
    }
    '''
