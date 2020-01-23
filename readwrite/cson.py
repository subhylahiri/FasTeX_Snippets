"""Write a CSON file
"""
from io import TextIOBase
from typing import Any
from numbers import Number


class CSONWriter():
    """Class for writing to a CSON file

    Parameters
    ----------
    file : io.TextIO
        Text file object for snippet `.cson` file.
    level : int, optional, default = 0
        Indent level of current entry.
    indent : int, optional, default = 4
        Number of spaces per indent level.
    """
    file: TextIOBase
    indent: int = 4
    level: int = 0

    def __init__(self, file: TextIOBase, indent: int = 4, level: int = 0):
        self.file = file
        self.indent = indent
        self.level = level

    def _indent(self):
        """Write an indent to a CSON file.
        """
        self.file.write(' ' * self.indent * self.level)

    def _write_strings(self, text: str):
        """Write a multi-line string to a CSON file.

        Parameters
        ----------
        text : str
            Multi-line string to write to `file`.
        """
        lines = text.splitlines()
        self.file.write('"""\n')
        for line in lines:
            self._indent()
            self.file.write(line + '\n')
        self._indent()
        self.file.write('"""\n')

    def write_str(self, text: str):
        """Write a string to a CSON file.

        Parameters
        ----------
        text : str
            String to write to `file`.
    """
        if '\n' in text:
            self._write_strings(text)
        else:
            self.file.write('"' + text + '"\n')

    def write_dict(self, thing: dict):
        """Write a dict to a CSON file.

        Parameters
        ----------
        thing : dict
            Dictionary to write to `file`.
        """
        self.file.write('\n')
        self.level += 1
        for key, value in thing.items():
            self._indent()
            self.file.write('"' + key + '": ')
            self.write_any(value)
        self.level -= 1
        # _indent(file, indent, level + '}\n')

    def write_num(self, value: Number):
        """Write a number to a CSON file.

        Parameters
        ----------
        value : Number
            Number to write to `file`.
        """
        self.file.write(f'{value}\n')

    def write_bool(self, value: bool):
        """Write a boolean to a CSON file.

        Parameters
        ----------
        value : bool
            Boolean to write to `file`.
        """
        if value:
            self.file.write('true\n')
        else:
            self.file.write('false\n')

    def write_null(self):
        """Write a null to a CSON file.
        """
        self.file.write('null\n')

    def write_list(self, array: list):
        """Write a list to a CSON file.

        Parameters
        ----------
        array : list
            List to write to `file`.
        """
        self.file.write('[\n')
        self.level += 1
        for element in array:
            self._indent()
            self.write_any(element)
        self.level -= 1
        self._indent()
        self.file.write(']\n')

    def write_any(self, data: Any):
        """Write piece of data to a CSON file.

        Parameters
        ----------
        file : io.TextIO
            Text file object for snippet `.cson` file.
        data : Any
            Thing to write to `file`.
        level : int, optional, default = 0
            Indent level of current entry.
        indent : int, optional, default = 4
            Number of spaces per indent level.
        """
        if isinstance(data, str):
            self.write_str(data)
        elif isinstance(data, dict):
            self.write_dict(data)
        elif isinstance(data, list):
            self.write_list(data)
        elif isinstance(data, Number):
            self.write_num(data)
        elif isinstance(data, bool):
            self.write_bool(data)
        elif isinstance(data, None):
            self.write_null()
        else:
            raise TypeError(f'Unknown type: {type(data)}.')


def dump(obj: Any, file: TextIOBase, indent=4):
    """Write to a CSON file.

    Parameters
    ----------
    obj : Any
        Thing to write to `file`.
    file : io.TextIO
        Text file object for snippet `.cson` file.
    indent : int, optional, default = 4
        Number of spaces per indent level.
    """
    cson_file = CSONWriter(file, indent)
    cson_file.write_any(obj)
