#!/usr/bin/python3

import json
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# cmdb_login = 'portal_monitoring'
cmdb_login = 'apvorobev'
# cmdb_password = 'e'
cmdb_password = ''


def json_read(json_object):
    print(json.dumps(json_object, sort_keys=True, indent=4))


def main():
    cmdb_api_url = "https://cmdb.common.gos-tech.xyz/rest/"

    url_opject = "https://cmdb.common.gos-tech.xyz/rest/objects/"

    url_types = "https://cmdb.common.gos-tech.xyz/rest/types/"

    url_catigories = "https://cmdb.common.gos-tech.xyz/rest/categories/3"

    '''
    create new type
    '''
    # response = requests.request("POST", url_types, headers=headers, data=payload)

    '''
    put type in categories
    '''

    # response = requests.request("PUT", url_catigories, headers=headers, data=payload)

    # print(response.status_code)
    # print(response.json())

    def cloud_api(api_name: str) -> dict:
        cloud_api_url = 'https://portal.gos.sbercloud.dev/api/v1/'

        # portal_token = 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI4NGE0OGQ1ZC03ODU5LTRiNzktOWVkYi01MDkyZTRmZjQ5ZmUifQ.eyJqdGkiOiIzNzU2ODVhZi03NGU5LTQ4NzItYWMxOC1iMDY2NzgxMzY1MjMiLCJleHAiOjAsIm5iZiI6MCwiaWF0IjoxNjI5NjUzMzIyLCJpc3MiOiJodHRwczovL2F1dGguZ29zLnNiZXJjbG91ZC5kZXYvYXV0aC9yZWFsbXMvUGxhdGZvcm1BdXRoIiwiYXVkIjoiaHR0cHM6Ly9hdXRoLmdvcy5zYmVyY2xvdWQuZGV2L2F1dGgvcmVhbG1zL1BsYXRmb3JtQXV0aCIsInN1YiI6ImQ4ODRjNzY4LTk5M2ItNDdjOS1hNWY1LTYxYWVlYzI5YTU4OSIsInR5cCI6Ik9mZmxpbmUiLCJhenAiOiJQbGF0Zm9ybUF1dGgtUHJveHkiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJkY2U4ZGMwNi0yMGFjLTQ3ZDgtODVlYS00ZWI4MWYyZjFhZDYiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsicGxhdGZvcm1hdXRoX3VzZXIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJzY29wZSI6Im9mZmxpbmVfYWNjZXNzIGVtYWlsIGVtcGxveWVlIGxvZ2luIn0.vssHBwFQh9QUwlQU-KTlPrlIKVDVJHNDhBPEytGrQvo'
        portal_token = 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI4NGE0OGQ1ZC03ODU5LTRiNzktOWVkYi01MDkyZTRmZjQ5ZmUifQ.eyJqdGkiOiIxZWNiMTI3MC01OTFhLTQ3NzUtOGM0YS01YjlmMzYyMTk0MTIiLCJleHAiOjAsIm5iZiI6MCwiaWF0IjoxNjMwMDA4MjM5LCJpc3MiOiJodHRwczovL2F1dGguZ29zLnNiZXJjbG91ZC5kZXYvYXV0aC9yZWFsbXMvUGxhdGZvcm1BdXRoIiwiYXVkIjoiaHR0cHM6Ly9hdXRoLmdvcy5zYmVyY2xvdWQuZGV2L2F1dGgvcmVhbG1zL1BsYXRmb3JtQXV0aCIsInN1YiI6ImEyYTZiNTQwLWU0MTgtNDlmNC1hZGQ5LTcwOGEwYTE5NGUxMyIsInR5cCI6Ik9mZmxpbmUiLCJhenAiOiJQbGF0Zm9ybUF1dGgtUHJveHkiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiI4ZjFjMzQ0Yy0zNzllLTRmNjMtYTVjOC0zOWMyZjE2YzdiMTciLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsicGxhdGZvcm1hdXRoX3VzZXIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJzY29wZSI6Im9mZmxpbmVfYWNjZXNzIGVtYWlsIGVtcGxveWVlIGxvZ2luIn0.zQkUaSg7egcD0guBF2yMgFY1rOfxi6M0iPX1R7_Si2g'

        headers = {
            'user-agent': 'SberTech',
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'authorization': 'Token %s' % portal_token}

        response = requests.get('%s%s' % (cloud_api_url, api_name), headers=headers, verify=False)
        return dict(stdout=json.loads(response.content), status_code=response.status_code)

    def cmdb_api(method: str, api_method: str = '', payload: dict = '', token: str = '') -> dict:
        headers_cmdb_api = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token
        }
        return json.loads(requests.request(method, cmdb_api_url + api_method, headers=headers_cmdb_api,
                                           data=json.dumps(payload)).content)

    def create_vm_objects(vm_info: dict, cmdb_token: str, type_id: str) -> dict:

        # print(vm_info['vm_name'])
        # print(vm_info['vm_id'])
        # print(vm_info['local_ip'])
        # print(vm_info['public_ip'])
        # print(vm_info['os_type'])
        # print(f"{vm_info['cpu']}/{vm_info['ram']}/{vm_info['disk']}")
        # print(vm_info['creator'])

        vm_object_template = {
            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": 17,
            "fields": [
                {
                    "name": "vm_name",
                    "value": vm_info['vm_name']
                },
                {
                    "name": "vm_id",
                    "value": vm_info['vm_id']
                },
                {
                    "name": "local_ip",
                    "value": vm_info['local_ip']
                },
                {
                    "name": "public_ip",
                    "value": vm_info['public_ip']
                },
                {
                    "name": "os_type",
                    "value": str(vm_info['os_type'])
                },
                {
                    "name": "hardware",
                    "value": f"{vm_info['cpu']}/{vm_info['ram']}/{vm_info['disk']}"
                },
                {
                    "name": "creator",
                    "value": vm_info['creator']
                }
            ]
        }
        print(vm_object_template)

        return cmdb_api('POST', 'object/', vm_object_template, cmdb_token)

    auth_payload = {
        "user_name": cmdb_login,
        "password": cmdb_password
    }

    # cmdb_token = cmdb_api('POST', 'auth/login', auth_payload)['token']
    # print(cmdb_token)
    cmdb_token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOnsiZXNzZW50aWFsIjp0cnVlLCJ2YWx1ZSI6IkRBVEFHRVJSWSJ9LCJpYXQiOjE2MzAyNzA1MjcsImV4cCI6MTYzMDM1NDUyNywiREFUQUdFUlJZIjp7ImVzc2VudGlhbCI6dHJ1ZSwidmFsdWUiOnsidXNlciI6eyJwdWJsaWNfaWQiOjE3fX19fQ.j3jsZJDSSU-wLkhjOiDPi4yF2zY--pfBudv1LZNY6i4FirBy5AKN_Whk6_Mf6h_WfycMpNFEcegCq5rVBgaPUY2xxmEtsHcrBYTmVq4E-dj663alFfM_n33tWdfpt_xEfoGCqhqjyVAEyrxGxvucr6v91Qwbz_1HO1q8-YXAHGxmHFhf7SYXlY-hXotbSPV1LTC0QF54A0pkuvoZV04TqN5ORCS6_-bjmjxDmXd93_5KxQYayd3qkGUy47LiCuP_IZ4rIGXI7Ixj1p4klfDpGupWjwDlH92MCRLc5hzcQJwY7B5sDMT_HxMWl_mNwXOH7fxj5bZrOldALZy278R12Q'

    from projects import cloud_projects

    # all_projects, all_projects_with_id = [], {}
    all_projects = {}

    for project in cloud_projects['stdout']['projects']:
        all_projects[project['name']] = project['id']

    del cloud_projects

    number_of_all_pages_types = cmdb_api('GET', 'types/', token=cmdb_token)['pager']['total_pages']

    all_types_pages, cmdb_projects = [], {}
    # all_types_pages, cmdb_projects = {}, {}

    for page in range(1, number_of_all_pages_types + 1):
        response_page = cmdb_api('GET', f'types/?page={page}', token=cmdb_token)
        all_types_pages.append(response_page)

        for cmdb_type in all_types_pages[page - 1]['results']:
            cmdb_projects[cmdb_type['label']] = cmdb_type['name']

    all_categories = cmdb_api('GET', 'categories/', token=cmdb_token)['pager']['total_pages']

    # categories = {'results': [{'public_id': 2, 'name': 'vcod-subnets', 'label': 'Vcod subnets',
    #                            'meta': {'icon': 'fab fa-battle-net', 'order': 1}, 'parent': None, 'types': [1]},
    #                           {'public_id': 3, 'name': 'passports', 'label': 'Паспорта',
    #                            'meta': {'icon': 'far fa-address-book', 'order': 2}, 'parent': None, 'types': [50]},
    #                           {'public_id': 13, 'name': 'vm-list-dev-ift', 'label': 'VM',
    #                            'meta': {'icon': 'far fa-folder-open', 'order': 1}, 'parent': 12, 'types': []},
    #                           {'public_id': 17, 'name': 'sizings', 'label': 'Сайзинги',
    #                            'meta': {'icon': 'far fa-folder-open', 'order': None}, 'parent': None, 'types': []},
    #                           {'public_id': 19, 'name': 'gostex', 'label': 'Гостех',
    #                            'meta': {'icon': 'far fa-folder-open', 'order': None}, 'parent': 17, 'types': [13, 14]}],
    #               'count': 5, 'total': 5,
    #               'parameters': {'limit': 10, 'sort': 'public_id', 'order': 1, 'page': 1, 'filter': {},
    #                              'optional': {'view': 'list'}}, 'pager': {'page': 1, 'page_size': 10, 'total_pages': 1},
    #               'pagination': {'current': 'http://cmdb.common.gos-tech.xyz/rest/categories/',
    #                              'first': 'http://cmdb.common.gos-tech.xyz/rest/categories/?page=1',
    #                              'prev': 'http://cmdb.common.gos-tech.xyz/rest/categories/?page=1',
    #                              'next': 'http://cmdb.common.gos-tech.xyz/rest/categories/?page=1',
    #                              'last': 'http://cmdb.common.gos-tech.xyz/rest/categories/?page=1'},
    #               'response_type': 'GET', 'model': 'Category', 'time': '2021-08-29T20:56:29.061493+00:00'}

    all_categories_pages = []
    for page in range(1, all_categories + 1):
        response_page = cmdb_api('GET', f'categories/?page={page}', token=cmdb_token)
        all_categories_pages.append(response_page)

    # all_categories_pages = [{'results': [{'public_id': 2, 'name': 'vcod-subnets', 'label': 'Vcod subnets',
    #                                       'meta': {'icon': 'fab fa-battle-net', 'order': 1}, 'parent': None,
    #                                       'types': [1]}, {'public_id': 3, 'name': 'passports', 'label': 'Паспорта',
    #                                                       'meta': {'icon': 'far fa-address-book', 'order': 2},
    #                                                       'parent': None, 'types': [50]},
    #                                      {'public_id': 13, 'name': 'vm-list-dev-ift', 'label': 'VM',
    #                                       'meta': {'icon': 'far fa-folder-open', 'order': 1}, 'parent': 12,
    #                                       'types': []}, {'public_id': 17, 'name': 'sizings', 'label': 'Сайзинги',
    #                                                      'meta': {'icon': 'far fa-folder-open', 'order': None},
    #                                                      'parent': None, 'types': []},
    #                                      {'public_id': 19, 'name': 'gostex', 'label': 'Гостех',
    #                                       'meta': {'icon': 'far fa-folder-open', 'order': None}, 'parent': 17,
    #                                       'types': [13, 14]}], 'count': 5, 'total': 5,
    #                          'parameters': {'limit': 10, 'sort': 'public_id', 'order': 1, 'page': 1, 'filter': {},
    #                                         'optional': {'view': 'list'}},
    #                          'pager': {'page': 1, 'page_size': 10, 'total_pages': 1},
    #                          'pagination': {'current': 'http://cmdb.common.gos-tech.xyz/rest/categories/?page=1',
    #                                         'first': 'http://cmdb.common.gos-tech.xyz/rest/categories/?page=1',
    #                                         'prev': 'http://cmdb.common.gos-tech.xyz/rest/categories/?page=1',
    #                                         'next': 'http://cmdb.common.gos-tech.xyz/rest/categories/?page=1',
    #                                         'last': 'http://cmdb.common.gos-tech.xyz/rest/categories/?page=1'},
    #                          'response_type': 'GET', 'model': 'Category', 'time': '2021-08-29T21:18:52.304628+00:00'}]

    for categorie in all_categories_pages:
        all_types_in_passports = list(filter(lambda x: x['name'] == 'passports', categorie['results']))[0]['types']

    for project in all_projects:
        if project not in cmdb_projects and project == 'gt-rosim-dev-customer':
            print(project)

            # data_type_template = {'fields': [{'type': 'text', 'name': 'vm_name', 'label': 'vm_name'},
            #                                  {'type': 'text', 'name': 'vm_id', 'label': 'vm_id'},
            #                                  {'type': 'text', 'name': 'local_ip', 'label': 'local_ip'},
            #                                  {'type': 'text', 'name': 'public_ip', 'label': 'public_ip'},
            #                                  {'type': 'text', 'name': 'hardware', 'label': 'hardware'},
            #                                  {'type': 'text', 'name': 'os_type', 'label': 'os_type'},
            #                                  {'type': 'text', 'name': 'creator', 'label': 'creator'}], 'active': True,
            #                       'version': '1.0.0', 'author_id': 17,
            #                       'render_meta': {'icon': 'fa fa-cube', 'sections': [
            #                           {'fields': ['vm_name', 'vm_id', 'local_ip', 'public_ip', 'os_type', 'hardware',
            #                                       'creator'],
            #                            'type': 'section', 'name': 'avorr', 'label': 'avorr'}], 'externals': [],
            #                                       'summary': {}},
            #                       'acl': {'activated': False}, 'name': 'avorr', 'label': 'avorr',
            #                       'description': 'avorr'}

            data_type_template = {'fields': [{'type': 'text', 'name': 'creator', 'label': 'creator'},
                                             {'type': 'text', 'name': 'hardaware', 'label': 'hardware'},
                                             {'type': 'text', 'name': 'oc_type', 'label': 'oc_type'},
                                             {'type': 'text', 'name': 'public_ip', 'label': 'public_ip'},
                                             {'type': 'text', 'name': 'local_ip', 'label': 'local_ip'},
                                             {'type': 'text', 'name': 'vm_id', 'label': 'vm_id'},
                                             {'type': 'text', 'name': 'vm_name', 'label': 'vm_name'}], 'active': True,
                                  'version': '1.0.0', 'author_id': 17,
                                  'render_meta': {'icon': 'fa fa-cube', 'sections': [
                                      {'fields': ['vm_name', 'vm_id', 'local_ip', 'public_ip', 'oc_type', 'hardaware',
                                                  'creator'],
                                       'type': 'section', 'name': 'test2', 'label': 'test2'}], 'externals': [],
                                                  'summary': {}},
                                  'acl': {'activated': False}, 'name': 'test2', 'label': 'test2',
                                  'description': 'test2'}


            data_type_template['render_meta']['sections'][0]['name'] = data_type_template['name'] = all_projects[
                project]
            data_type_template['render_meta']['sections'][0]['label'] = data_type_template['label'], data_type_template[
                'description'] = project, f'gt-vcod with id = {all_projects[project]}'

            print(data_type_template)

            create_type = cmdb_api('POST', 'types/', data_type_template, cmdb_token)

            print(create_type)

            new_all_types_pages = []
            for page in range(1, number_of_all_pages_types + 1):
                response_page = cmdb_api('GET', f'types/?page={page}', token=cmdb_token)
                new_all_types_pages.append(response_page)

            new_type_id = None
            for new_types in new_all_types_pages:
                for new_item in new_types['results']:
                    if new_item['name'] == all_projects[project]:
                        new_type_id = new_item['public_id']

            print(new_type_id)

            data_cat_template = {'public_id': 3, 'name': 'passports', 'label': 'Паспорта',
                                 'meta': {'icon': 'far fa-address-book', 'order': 2}, 'parent': None,
                                 # 'types': [27, 19, 11, 12, 5]}
                                 'types': []}
            print(all_types_in_passports)
            data_cat_template['types'] = all_types_in_passports
            data_cat_template['types'].append(new_type_id)

            print(data_cat_template)

            put_type_in_catigories = cmdb_api('PUT', 'categories/3', data_cat_template, cmdb_token)

            vm_list = cloud_api(f'servers?project_id={all_projects[project]}')

            check_public_ip = lambda x, y: y[x]['address'] if x in y else ''

            for server in vm_list['stdout']['servers']:
                #     disk = ''
                #     if server['volumes'] != None:
                #         for volume in range(len(server['volumes'])):
                #             foo = check_volumes(server['volumes'], volume)
                #             disk = f'{disk}, {foo}'

                disks = ''
                if server['volumes']:
                    sum_disks = lambda x, y: f"{disks}{x[y]['size']},"
                    for item in range(len(server['volumes'])):
                        disks = sum_disks(server['volumes'], item)

                # vm_info = {
                #     'vm_id': server['id'],
                #     'vm_name': server['service_name'],
                #     'vm_server': server['name'],
                #     'oc_type': server['os_version'],
                #     'creator': server['creator_login'],
                #     'local_ip': server['outputs']['server_ip'],
                #     'public_ip': check_public_ip('public_ip', server),
                #     'disk': disks[2:]
                # }

                vm_info = {
                    'vm_name': server['service_name'],
                    'vm_id': server['id'],
                    'vm_server': server['name'],
                    'local_ip': server['outputs']['server_ip'],
                    'public_ip': check_public_ip('public_ip', server),
                    'os_type': server['os_version'],
                    'cpu': server['cpu'],
                    'ram': server['ram'],
                    'disk': disks[:-1],
                    'creator': server['creator_login']
                }

                create_object = create_vm_objects(vm_info, cmdb_token, new_type_id)
                # print(create_object)
                json_read(create_object)
                time.sleep(2)

    # test_create_vm = {'status': True, 'type_id': 54, 'version': '1.0.0', 'author_id': 17,
    #                   'fields': [{'name': 'vm_name', 'value': 'd-infra-vpn-02'},
    #                              {'name': 'vm_id', 'value': '642362c8-e729-4acc-b1fa-1e4a52989da1'},
    #                              {'name': 'local_ip', 'value': '172.27.118.111'},
    #                              {'name': 'public_ip', 'value': '37.18.112.134'}, {'name': 'os_type', 'value': '7.7'},
    #                              {'name': 'hardware', 'value': '2/4/'},
    #                              {'name': 'creator', 'value': 'ddkibardin@sberbank.ru'}]}
    #
    # test_create = cmdb_api('POST', 'object/', test_create_vm, cmdb_token)
    #
    # print(test_create)

    # print(json_read(vm_info))
    # print(vm_info)
    # print('****' * 30)
    # print(server['id'])
    # print(server['service_name'])
    # print(server['name'])
    # print(server['os_version'])
    # print(server['creator_login'])
    # print(server['outputs']['server_ip'])
    # if 'public_ip' in server:
    #     print(server['public_ip'])
    # else:

    # print(server['volumes'])

    # print(vm_list)
    # print(put_type_in_catigories)

    # response = requests.request("PUT", url_catigories, headers=headers, data=payload)

    # response = requests.request("POST", url_types, headers=headers, data=payload)


# all_projects = (project for project in all_projects if project.startswith('gt-'))

# for ii in all_projects:
#     print(ii)

# print(all_types_pages['results'])
# print(i)
# json_read(all_types_pages[page - 1]['results'])
# for i in all_types_pages[page - 1]:
#     print(i)
# print(all_types_pages[page]['description'])
# print(json_read(all_types_pages[0]))

# json_read(number_of_all_pages_types)
# print(all_projects)
# print(all_projects_with_id)


if __name__ == '__main__':
    main()
