#!/usr/bin/python3

from pymongo import MongoClient


def get_dg_objects():
    with open('allObjects.py', 'w') as file:
        mongo_db = MongoClient('mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb')['cmdb']
        # mongo_db = MongoClient('mongodb://admin:nk63QXkzCW@172.26.107.101:30039/cmdb?authSource=admin')
        dg_objects = mongo_db.get_collection('framework.objects')
        all_objects = tuple(dg_objects.find())
        file.write('import datetime\nfrom bson.objectid import ObjectId\nall_objects = %s\n' % repr(all_objects))


if __name__ == '__main__':
    get_dg_objects()
