"""Write a CSON file
"""
from io import TextIOBase
from typing import Union
from numbers import Number
from collections.abc import Iterable, Mapping
from contextlib import contextmanager
CSONable = Union[None, bool, Number, Iterable, Mapping, str]


class CSONWriter():
    """Class for writing to a CSON file

    Parameters
    ----------
    file : io.TextIO
        Text file object for snippet `.cson` file.
    indent : int, optional, default = 4
        Number of spaces per indent level.
    level : int, optional, default = 0
        Indent level of current entry.
    """
    file: TextIOBase
    indent: int = 4
    level: int = 0
    parent: str

    def __init__(self, file: TextIOBase, indent: int = 4, level: int = 0):
        self.file = file
        self.indent = indent
        self.level = level
        self.parent = ''

    @contextmanager
    def indented(self, parent: str):
        """Context manager for one level deeper indent

        Parameters
        ----------
        parent : str
            type of thing at one level up indent
        """
        old_parent = self.parent
        self.parent = parent
        self.level += 1
        try:
            yield
        finally:
            self.level -= 1
            self.parent = old_parent

    def write_raw(self, text: str, started: bool = False, ended: bool = False):
        """Write raw text to a CSON file.

        Parameters
        ----------
        text : str
            Contents of line to be written.
        started : bool, optional
            Indent before writing? By default False.
        ended : bool, optional
            New line after writing? By default False.
        """
        if started:
            text = (' ' * (self.indent * self.level)) + text
        if ended:
            text += '\n'
        if text:
            self.file.write(text)

    def write_str(self, text: str):
        """Write a string to a CSON file.

        Parameters
        ----------
        text : str
            String to write to `self.file`.
        """
        if '\n' in text:
            self.write_raw('"""', ended=True)
            for line in text.splitlines():
                self.write_raw(line, True, True)
            self.write_raw('"""', True)
        else:
            self.write_raw('"' + text + '"')

    def write_num(self, value: Number):
        """Write a number to a CSON file.

        Parameters
        ----------
        value : Number
            Number to write to `self.file`.
        """
        self.write_raw(str(value))

    def write_bool(self, value: bool):
        """Write a boolean to a CSON file.

        Parameters
        ----------
        value : bool
            Boolean to write to `self.file`.
        """
        if value:
            self.write_raw('true')
        else:
            self.write_raw('false')

    def write_null(self):
        """Write a null to a CSON file.
        """
        self.write_raw('null')

    def write_dict(self, thing: dict):
        """Write a dict to a CSON file.

        Parameters
        ----------
        thing : dict
            Dictionary to write to `self.file`.
        """
        remaining = len(thing)
        if self.parent == 'list':
            self.write_raw('{', ended=True)
            remaining += 1
        elif self.parent == 'dict':
            self.write_raw('', ended=True)
        with self.indented('dict'):
            for key, value in thing.items():
                remaining -= 1
                self.write_raw(f'"{key}": ', True, False)
                self.write(value, False, remaining)
        if self.parent == 'list':
            self.write_raw('}', True)
        else:
            self.write_raw('', False)

    def write_list(self, array: list):
        """Write a list to a CSON file.

        Parameters
        ----------
        array : list
            List to write to `self.file`.
        """
        self.write_raw('[', ended=True)
        with self.indented('list'):
            for element in array:
                self.write(element, True, True)
        self.write_raw(']', True)

    def write(self, data: CSONable, started: bool = False, ended: bool = True):
        """Write piece of data to a CSON file.

        Parameters
        ----------
        data : CSONable = Union[None, bool, Number, Iterable, Mapping, str]
            Thing to write to `self.file`.
        started : bool, optional
            Indent before writing? By default False
        ended : bool, optional
            New line after writing? By default True.
        """
        self.write_raw('', started, False)
        if isinstance(data, str):
            self.write_str(data)
        elif isinstance(data, Mapping):
            self.write_dict(data)
        elif isinstance(data, Iterable):
            self.write_list(data)
        elif isinstance(data, Number):
            self.write_num(data)
        elif isinstance(data, bool):
            self.write_bool(data)
        elif data is None:
            self.write_null()
        else:
            raise TypeError(f'Unknown data type: {type(data)}.')
        self.write_raw('', False, ended)


def dump(obj: CSONable, file: TextIOBase, indent: int = 4, level: int = 0):
    """Write to a CSON file.

    Parameters
    ----------
    obj : CSONable = Union[None, bool, Number, Iterable, Mapping, str]
        Thing to write to `file`.
    file : io.TextIO
        Text file object for snippet `.cson` file.
    indent : int, optional, default = 4
        Number of spaces per indent level.
    level : int, optional, default = 0
        Indent level of `obj`. If `obj` is a `dict` choose `-1` if you want its
        entries to have 0 indent.
    """
    cson_file = CSONWriter(file, indent, level)
    cson_file.write(obj)
