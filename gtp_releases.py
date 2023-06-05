#!/usr/local/bin/python3

# import json
import time
# import socket
import requests
# from functools import reduce
# from datetime import datetime
# from pymongo import MongoClient
# from docx.api import Document
from requests.auth import HTTPBasicAuth

# from tools import *
from env import portal_info
from common_function import dg_api
from common_function import category_id
from common_function import get_dg_token
from common_function import get_mongodb_objects

# from vm_passport import get_all_jsons

# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# from requests.packages.urllib3.exceptions import InsecureRequestWarning

docx_url: str = "https://base.sw.sbc.space/wiki/plugins/servlet/scroll-office/api/artifacts"
version_urls: dict = {
    "Solution-1.1": "%s/84452538-9712-4ac9-a521-6c5719c2c743/Solution v 1.1-v84-20220220_115446.docx" % docx_url,
    "Solution-1.2": "%s/0d54ae16-e6e1-4f4d-b608-4b7c1ad028e9/Solution v 1.2-v8-20220220_115543.docx" % docx_url
}


def download_docx_files() -> None:
    """
    Func to download docx files from confluence
    :return: None
    """
    from env import cf_login, cf_password
    for version in version_urls:
        response = requests.get(version_urls[version], auth=HTTPBasicAuth(cf_login, cf_password))
        with open('%s.docx' % version, 'wb') as file:
            file.write(response.content)


download_docx_files()


def read_docx(docx_file_name: str) -> list:
    """
    Func to get table from docx
    :param docx_file_name:
    :return: list
    """
    document = Document('%s.docx' % docx_file_name)
    table = document.tables[1]
    data = list()

    keys = None

    for i, row in enumerate(table.rows):
        text = (cell.text for cell in row.cells)
        if i == 0:
            keys = tuple(text)
            continue
        row_data = dict(zip(keys, text))
        data.append(row_data)
    return data


def releases() -> None:
    """
    main func for create type with platform release version in DataGerry
    :return: None
    """

    def create_object(version_info: dict, dg_token: str, type_id: int, author_id: int, method: str = 'POST',
                      template: bool = False) -> dict:
        if method == 'PUT':
            # return dg_api(method, f'object/{version_info["public_id"]}', dg_token, version_info)
            print(f'object/{version_info["public_id"]}')

        release_object_template: dict = {

            "status": True,
            "type_id": type_id,
            "version": "1.0.0",
            "author_id": author_id,
            "fields": [
                {
                    "name": "platform-path",
                    "value": version_info['Platform Part'].strip()
                },
                {
                    "name": "tribe",
                    "value": version_info['Tribe'].strip()
                },
                {
                    "name": "service-code",
                    "value": version_info['Service Code'].strip()

                },
                {
                    "name": "ke",
                    "value": version_info['KE'].strip()
                },
                {
                    "name": "service-name",
                    "value": version_info['Service Name'].strip()
                },
                {
                    "name": "marketing-name",
                    "value": version_info['Marketing Service Name'].strip()
                },
                {
                    "name": "distrib-link",
                    "value": version_info['Distrib Link'].strip()
                }
            ]
        }

        if template:
            return release_object_template

        return dg_api('POST', 'object/', dg_token, release_object_template)

    dg_token, user_id = get_dg_token()
    all_categories: tuple = get_mongodb_objects('framework.categories')

    platform_releases_category_id = \
        category_id('platform-releases', 'Platform Releases', 'fas fa-list-alt', dg_token, all_categories)

    # all_pprb3_verions: dict = json.loads(requests.request("GET", portal_info['app_versions']).content)

    # cmdb_projects = get_all_jsons('types', dg_token)

    cmdb_projects: tuple = get_mongodb_objects('framework.types')

    for docx in version_urls:
        if not any(tuple(map(lambda y: y['name'] == docx.replace('.', '_'), cmdb_projects))):

            data_type_template: dict = {
                "fields": [
                    {
                        "type": "text",
                        "name": "platform-path",
                        "label": "Platform Part"
                    },
                    {
                        "type": "text",
                        "name": "tribe",
                        "label": "Tribe"
                    },
                    {
                        "type": "text",
                        "name": "service-code",
                        "label": "Service Code"
                    },
                    {
                        "type": "text",
                        "name": "ke",
                        "label": "KE"
                    },
                    {
                        "type": "text",
                        "name": "service-name",
                        "label": "Service Name"
                    },
                    {
                        "type": "text",
                        "name": "marketing-name",
                        "label": "Marketing Service Name"
                    },
                    {
                        "type": "text",
                        "name": "distrib-link",
                        "label": "Distrib Link"
                    }
                ],
                "active": True,
                "version": "1.0.0",
                "author_id": user_id,
                "render_meta": {
                    "icon": "fas fa-file-alt",
                    "sections": [
                        {
                            "fields": [
                                "platform-path",
                                "tribe",
                                "service-code",
                                "ke",
                                "service-name",
                                "marketing-name",
                                "distrib-link"
                            ],
                            "type": "section",
                            "name": docx.replace('.', '_'),
                            "label": docx
                        }
                    ],
                    "externals": [],
                    "summary": {
                        "fields": [
                            "platform-path",
                            "tribe",
                            "service-code",
                            "ke",
                            "service-name",
                            "marketing-name",
                            "distrib-link"
                        ]
                    }
                },
                "acl": {
                    "activated": True,
                    "groups": {
                        "includes": {
                            "1": [
                                "CREATE",
                                "READ",
                                "UPDATE",
                                "DELETE"
                            ],
                            "2": [
                                "READ"
                            ]
                        }
                    }
                },
                "name": docx.replace('.', '_'),
                "label": docx,
                "description": docx
            }
            create_type = dg_api('POST', 'types/', dg_token, data_type_template)
            print(create_type)

            print(create_type['result_id'], 'new type id')

            data_cat_template: dict = {
                "public_id": platform_releases_category_id['public_id'],
                "name": platform_releases_category_id['name'],
                "label": platform_releases_category_id['label'],
                "meta": {
                    "icon": "fas fa-list-alt",
                    "order": None
                },
                "parent": None,
                "types": platform_releases_category_id['types']
            }

            if not create_type['result_id']:
                return
            data_cat_template['types'].append(create_type['result_id'])
            put_type_in_catigories = dg_api('PUT', f"categories/{platform_releases_category_id['public_id']}",
                                              dg_token,
                                              data_cat_template)

            print('PUT TYPE IN CATIGORIES', put_type_in_catigories)

            release_info: list = read_docx(docx)

            for version in release_info:
                create_version_objects = create_object(version, dg_token, create_type['result_id'], user_id)
                print('CREATE OBJECT', create_version_objects)
                #time.sleep(0.1)

    all_objects: tuple = get_mongodb_objects('framework.objects')
    # cmdb_projects = get_all_jsons('types', dg_token)
    # allTypesVersions = reduce(lambda x, y: x + y, map(lambda foo: tuple(
    #     filter(lambda bar: f'pprb3-versions-{portal_name}--' in bar['name'], foo['results'])), cmdb_projects))


if __name__ == '__main__':
    releases(next(iter(portal_info)))

#
# def pages():
#     pages_url: str = "https://base.sw.sbc.space/wiki/rest/api/content?type=page&start=0&limit=99999"
#     pages_url: str = "https://base.sw.sbc.space/wiki/rest/api/space/PLTFM/content?start=0&limit=9999&type=page"
#     pages_url: str = "https://base.sw.sbc.space/wiki/rest/api/space/PLTFM/content?start=0&limit=9999"
#     return json.loads(requests.get(pages_url, auth=HTTPBasicAuth('tuz_pid_tuz_pid_jira', '3988hUaRWg!!M*')).content)
#
#
# foo = pages()
#
# for i in foo['page']['results']:
#     # print(i['title'])
#     if i['title'] == 'Департамент развития':
#         json_read(i)
# # for i in foo['results']:
# #     print(i['title'])
# # print(foo.content)
# exit()


# def download_docx():
#     word_url = "https://base.sw.sbc.space/wiki/plugins/servlet/scroll-office/api/artifacts/776bf46b-e4ce-45e5-b6d3-1c2e1d58dedf/Состав поставки, Solution Гостех v 1.2 (draft)-v2-20220213_191910.docx"
#     pdf_url = "https://base.sw.sbc.space/wiki/download/temp/pdfexport-20220213-130222-1908-37/58494121_431cd746d33f433da86333aa04c35ddd-130222-1908-38.pdf?contentType=application/pdf"
# payload = json.dumps({
#     "pageId": "58494121",
#     "pageSet": "current",
#     "templateId": "com.k15t.scroll.office.default-template-1",
#     "properties": {
#         "labels": {
#             "includeContentWithLabels": [],
#             "excludeContentWithLabels": [],
#             "indexTerms": []
#         },
#         "content": {
#             "links": [
#                 "enableExternalLinks",
#                 "enableConfluenceLinks"
#             ],
#             "images": "fullResolution",
#             "advanced": "enableHeadingPromotion",
#             "comalaWorkflows": []
#         },
#         "macros": {
#             "macros": [
#                 "showTocOutput",
#                 "showChildrenOutput"
#             ]
#         },
#         "title": {
#             "figure": "after",
#             "table": "after"
#         },
#         "printOptions": {
#             "artifactFileName": "<span contenteditable=\"false\" draggable=\"false\" class=\"template-placeholder\" data-placeholder-app-key=\"com.k15t.scroll.pdf\" data-placeholder-key=\"document-title\" data-placeholder-velocity=\"${document.title}\" data-placeholder-name=\"Document Title\" data-placeholder-properties=\"{}\">Document Title</span>-v<span contenteditable=\"false\" draggable=\"false\" class=\"template-placeholder\" data-placeholder-app-key=\"com.k15t.scroll.pdf\" data-placeholder-key=\"document-revision\" data-placeholder-velocity=\"${document.rootPage.revision}\" data-placeholder-name=\"Document Revision\" data-placeholder-properties=\"{}\">Document Revision</span>-<span contenteditable=\"false\" draggable=\"false\" class=\"template-placeholder\" data-placeholder-app-key=\"com.k15t.scroll.pdf\" data-placeholder-key=\"export-date\" data-placeholder-velocity=\"${export.date(&amp;#x22;YYYMMdd_HHmmss&amp;#x22;)}\" data-placeholder-name=\"Export Date (YYYMMdd_HHmmss)\" data-placeholder-properties=\"{&amp;#x22;pattern&amp;#x22;:&amp;#x22;YYYMMdd_HHmmss&amp;#x22;}\">Export Date (YYYMMdd_HHmmss)</span>"
#         },
#         "locale": {
#             "defaultLocale": "en"
#         },
#         "tables": {
#             "tableFit": "AUTO_FIT_TO_WINDOW"
#         }
#     },
#     "pageOptions": {},
#     "locale": "ru-RU",
#     "debugMode": False
# })
# headers = {
#     'Authorization': 'Basic YXB2b3JvYmV2OlNhc2hhd29ybGRkMTEh',
#     'Content-Type': 'application/json',
#     'Cookie': 'JSESSIONID=CB6437D1E62536255D729D9A462E0440'
# }
# response = requests.request("GET", word_url, headers=headers, data=payload)
# with open('platform-versions.docx', 'wb') as f:
#     f.write(response.content)
# download_docx()


# def check_resolves(dns_name: str) -> bool:
#     """function for checking resolving dns names"""
#     try:
#         socket.gethostbyname(dns_name)
#         return True
#     except socket.error as Error:
#         print(dns_name, Error)
#         return False


# document = Document('platform-versions.docx')

# table = document.tables[1]

# data = []
# keys = None
# for i, row in enumerate(table.rows):
#     text = (cell.text for cell in row.cells)
#     if i == 0:
#         keys = tuple(text)
#         continue
#     row_data = dict(zip(keys, text))
#     data.append(row_data)


# for i in data:
#     print(i.keys())
