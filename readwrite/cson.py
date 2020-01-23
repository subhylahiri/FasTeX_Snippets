"""Write CSON file
"""
from io import TextIOBase
from typing import Any

INDENT = '    '


def dump_str(file: TextIOBase, text: str):
    """Write a string to CSON file
    """
    file.write('"' + text + '"\n')
    file.flush()


def dump_list(file: TextIOBase, array: list, indent: int = 0):
    """Write a list to CSON file
    """
    file.write('[\n')
    file.flush()
    for element in array:
        file.write(INDENT * (indent + 1))
        dump(file, element, indent + 1)
    file.write(INDENT * indent + ']\n')
    file.flush()


def dump_dict(file: TextIOBase, structure: dict, indent: int = 0):
    """Write a dict to CSON file
    """
    file.write('{\n')
    file.flush()
    for key, value in structure.items():
        file.write(INDENT * (indent + 1))
        file.write('"' + key + '": ')
        dump(file, value, indent + 1)
    file.write(INDENT * indent + '}\n')
    file.flush()


def dump(file: TextIOBase, data: Any, indent: int = 0):
    """Write piece of data to CSON file
    """
    if isinstance(data, str):
        dump_str(file, data)
    elif isinstance(data, list):
        dump_list(file, data, indent)
    elif isinstance(data, dict):
        dump_dict(file, data, indent)
