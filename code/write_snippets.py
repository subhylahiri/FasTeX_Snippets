"""Write snippets in the relevant form for vscode/latex-utilities/atom
"""
import io
import re
import json
from typing import Union, List, Dict, Sequence

Body = Union[str, List[str]]
Snippet = Dict[str, Body]

TAB_STOP = re.compile(r'[^\\]\$(\d)')


def count_tabs(body: Body) -> int:
    """Count tab stops in snippet body.
    
    Parameters
    ----------
    body: Body = str or List[str]
        Body of snippet with tabstops `$1`,...,`$n`.
    
    Returns
    -------
    count : int
        Number of distinct tab stops in body.
    """
    if isinstance(body, list):
        return max((count_tabs(line) for line in body), default=0)
    tabs = TAB_STOP.findall(body)
    return max((int(num) for num in tabs), default=0)


def convert_body_vsc(body: Body, endtab: bool = False, maxtab: int = 0) -> Body:
    """Convert tab stops for a VSCode snippet
    
    Parameters
    ----------
    body: Body = str or List[str]
        Body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.
    
    Returns
    -------
    body: Body = str or List[str]
        Body of snippet with tabstops: `if endtab:` `$1`,...,`$n`,
        `else:` `$1`,...,`$n-1`,`$0`.
    """
    if isinstance(body, list):
        return [convert_body_vsc(line, endtab, maxtab) for line in body]
    if endtab or maxtab == 0:
        return body
    return re.sub(fr'[^\\]\${maxtab}', '$0', body)


def convert_snippet_vsc(snippet: Snippet, prefix: str = '', suffix: str = '',
                        endtab: bool = False) -> Snippet:
    """Convert a snippet from internal to VSCode format.
    
    Parameters
    ----------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, description.
    
    Returns
    -------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, description.
    """
    maxtab = 0
    if not endtab:
        maxtab = count_tabs(snippet['body'])
    vsc_prefix = prefix + snippet['prefix'] + suffix
    vsc_body = convert_body_vsc(snippet['body'], endtab, maxtab)
    return {'prefix': vsc_prefix, 'body': vsc_body,
            'description': snippet['description']}


def convert_body_atom(body: Body, endtab: bool = True, maxtab: int = 0) -> Body:
    """Convert body for an Atom snippet
    
    Parameters
    ----------
    body: Body = str or List[str]
        Body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.
    
    Returns
    -------
    body: Body = str or List[str]
        Body of snippet with tabstops: `if endtab:` `$1`,...,`$n`,
        `else:` `$1`,...,`$n-1`,`$0`.
    """
    if isinstance(body, str):
        if endtab and maxtab:
            return body + f'${maxtab + 1}'
        return body
    if endtab and maxtab:
        return '\n'.join(body + [f'${maxtab + 1}'])
    return '\n'.join(body)


def convert_snippet_atom(snippet: Snippet, prefix: str = '', suffix: str = '',
                         endtab: bool = False) -> Snippet:
    """Convert a snippet from internal to VSCode format.
    
    Parameters
    ----------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, description.
    
    Returns
    -------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, description.
    """
    maxtab = 0
    if not endtab:
        maxtab = count_tabs(snippet['body'])
    atom_prefix = prefix + snippet['prefix'] + suffix
    atom_body = convert_body_atom(snippet['body'], endtab, maxtab)
    return {'prefix': atom_prefix, 'body': atom_body}
