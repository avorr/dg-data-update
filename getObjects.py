#!/usr/bin/python3

from pymongo import MongoClient

def getObjectsDb():
    with open('allObjects.py', 'w') as objectsFile:
        connection_sring = 'mongodb://p-infra-bitwarden-01.common.novalocal:27017/cmdb'
        cluster = MongoClient(connection_sring)
        db = cluster['cmdb']
        bdObjects = db.get_collection('framework.objects')
        all_objects = tuple(bdObjects.find({}))
        objectsFile.write('import datetime\nfrom bson.objectid import ObjectId\nall_objects = %s\n' % repr(all_objects))

if __name__ == '__main__':
    getObjectsDb()