#!/usr/bin/python3

import json
from pymongo import MongoClient

def echo(variable) -> None:
    """
    function to print variable name and value one
           call example:
                echo(f"{var=}")
    :param variable:
    :return: None
    """
    print(variable)
    # separator: int = variable.index('=')
    # print("%s = %s (##### Variable name, Value)" % (variable[:separator], variable[separator + 1:]))


def json_read(json_variable: dict) -> None:
    """
    function to read json
    :param json_variable:
    :return: None
    """
    print(json.dumps(json_variable, indent=4))


def write_to_file(variable: str) -> None:
    """
    function to write a variable to a file
       call example:
                write_to_file(f"{var=}")
    :param variable:
    :return: None
    """
    separator: int = variable.index('=')
    with open('%s.py' % variable[:separator], 'w') as file:
        file.write('%s = %s' % (variable[:separator], variable[(separator + 1):]))
