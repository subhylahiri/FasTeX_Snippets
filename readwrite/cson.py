"""Write a CSON file
"""
from io import TextIOBase
from typing import Any
from numbers import Number


def write_strings(file: TextIOBase, text: str, level: int = 0, indent: int = 4):
    """Write a multi-line string to a CSON file
    """
    lines = text.splitlines()
    file.write('"""\n')
    for line in lines:
        file.write(' ' * indent * level)
        file.write(line + '\n')
    file.write(indent * level)
    file.write('"""\n')


def write_str(file: TextIOBase, text: str, level: int = 0, indent: int = 4):
    """Write a string to a CSON file
    """
    if '\n' in text:
        write_strings(file, text, level, indent)
    else:
        file.write('"' + text + '"\n')


def write_dict(file: TextIOBase, thing: dict, level: int = 0, indent: int = 4):
    """Write a dict to a CSON file
    """
    file.write('\n')
    for key, value in thing.items():
        file.write(' ' * indent * (level + 1))
        file.write('"' + key + '": ')
        write_any(file, value, level + 1)
    # file.write(' ' * indent * level + '}\n')


def write_num(file: TextIOBase, value: Number):
    """Write a number to a CSON file
    """
    file.write(f'{value}\n')


def write_bool(file: TextIOBase, value: bool):
    """Write a boolean to a CSON file
    """
    if value:
        file.write('true\n')
    else:
        file.write('false\n')


def write_null(file: TextIOBase):
    """Write a null to a CSON file
    """
    file.write('null\n')


def write_list(file: TextIOBase, array: list, level: int = 0, indent: int = 4):
    """Write a list to a CSON file.
    """
    file.write('[\n')
    for element in array:
        file.write(' ' * indent * (level + 1))
        write_any(file, element, level + 1)
    file.write(' ' * indent * level + ']\n')


def write_any(file: TextIOBase, data: Any, level: int = 0, indent: int = 4):
    """Write piece of data to a CSON file.
    """
    if isinstance(data, str):
        write_str(file, data, level, indent)
    elif isinstance(data, dict):
        write_dict(file, data, level, indent)
    elif isinstance(data, list):
        write_list(file, data, level, indent)
    elif isinstance(data, Number):
        write_num(file, data)
    elif isinstance(data, bool):
        write_bool(file, data)
    elif isinstance(data, None):
        write_null(file)
    else:
        raise ValueError(f'Unknown type: {type(data)}.')


def dump(obj: Any, file: TextIOBase, indent=4):
    """Write to a CSON file.
    """
    write_any(file, obj, 0, indent)
