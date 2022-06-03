#!/usr/local/bin/python3

import json


def json_read(json_variable: dict) -> None:
    """
    function to read json
    :param json_variable:
    :return: None
    """
    print(json.dumps(json_variable, indent=4, default=str))


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
