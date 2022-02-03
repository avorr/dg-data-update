import json


def jsonRead(json_object: dict):
    print(json.dumps(json_object, indent=4))

def writeToFile(object: str):
    separator: int = object.index('=')
    with open('%s.py' % object[:separator], 'w') as file:
        file.write('%s = %s' % (object[:separator], object[(separator + 1):]))


