"""Write snippets in the relevant form for vscode/latex-utilities/atom

Functions
---------
read_data_json
    Import FasTeX snippet data in internal format.
convert_vscode
    Convert snippet data to VS Code snippet format.
convert_atom
    Convert snippet data to Atom snippet format.
convert_live
    Convert snippet data to VS Code LaTeX-Utilities live snippet format.
convert_vscode
    Convert multiline snippet data to VS Code snippet format
    and single-line snippet data to LaTeX-Utilities live snippet format.
make_snippet_json
    Write snippet data to a `.json` file.
"""
import re
import json
from typing import Union, List, Dict, Optional
if __name__ == "__main__":
    import cson
else:
    from . import cson

Body = Union[str, List[str]]
Snippet = Dict[str, Body]
SnippetDict = Dict[str, Snippet]
AtomSnippetDict = Dict[str, SnippetDict]

TAB_STOP = re.compile(r'(?<!\\)\$(\d)')


def count_tabs(body: Body) -> int:
    """Count tab stops in snippet body.

    Parameters
    ----------
    body : Body = str or List[str]
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


def body_append(body: Body, addendum: str) -> Body:
    """Add something to end of snippet
    """
    if isinstance(body, list):
        return body + [addendum]
    return body + addendum


def body_prepend(body: Body, addendum: str) -> Body:
    """Add something to start of snippet
    """
    if isinstance(body, list):
        return [addendum] + body
    return addendum + body


def convert_body_vsc(body: Body, endtab: bool = True, maxtab: int = 0) -> Body:
    """Convert tab stops for a VSCode snippet

    Parameters
    ----------
    body : Body = str or List[str]
        Body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.

    Returns
    -------
    body : Body = str or List[str]
        Body of snippet with tabstops: `if endtab:` `$1`,...,`$n`,
        `else:` `$1`,...,`$n-1`,`$0`.
    """
    if isinstance(body, list):
        return [convert_body_vsc(line, endtab, maxtab) for line in body]
    if endtab or maxtab == 0:
        return body
    return re.sub(fr'[^\\]\${maxtab}', '$0', body)


def convert_snippet_vsc(snippet: Snippet, prefix: str = '', suffix: str = '',
                        endtab: bool = True) -> Snippet:
    """Convert a snippet from internal to VSCode format.

    Parameters
    ----------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, description.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

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
    body : Body = str or List[str]
        Body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.

    Returns
    -------
    body : Body = str or List[str]
        Body of snippet with tabstops: `if endtab:` `$1`,...,`$n`,
        `else:` `$1`,...,`$n-1`,`$0`.
    """
    if endtab and maxtab:
        body = body_append(body, f'${maxtab + 1}')
    if isinstance(body, list):
        return '\n'.join(body)
    return body


def convert_snippet_atom(snippet: Snippet, prefix: str = '', suffix: str = '',
                         endtab: bool = True) -> Snippet:
    """Convert a snippet from internal to Atom format.

    Parameters
    ----------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, description.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

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


def convert_trigger_live(trigger: str,
                         prefix: str = '',
                         suffix: str = '  ') -> str:
    """Convert tab stops for a LaTeX-Utilities live snippet

    Parameters
    ----------
    trigger : str
        Trigger string for snippet.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.

    Returns
    -------
    trigger : str
        Trigger string for snippet, formatted for live snippets.
    """
    return r'(^|[^\\])' + prefix + trigger + suffix


def _help_body_live(body: str, endtab: bool = True, maxtab: int = 0) -> str:
    """Convert tab stops for one line of a live snippet

    Parameters
    ----------
    body : str
        Line of body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.

    Returns
    -------
    body : str
        Line of body of snippet with tabstops: `if endtab:` `$$1`,...,`$$n`,
        `else:` `$$1`,...,`$$n-1`,`$0`.
    """
    if not endtab or maxtab:
        body = re.sub(fr'[^\\]\${maxtab}', '$0', body)
    return TAB_STOP.sub('$$\1', body)


def convert_body_live(body: Body, endtab: bool = True, maxtab: int = 0) -> Body:
    """Convert tab stops for a VSCode live snippet

    Parameters
    ----------
    body : str
        Body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.

    Returns
    -------
    body : str
        Body of snippet with tabstops: `if endtab:` `$$1`,...,`$$n`,
        `else:` `$$1`,...,`$$n-1`,`$0`.
    """
    if isinstance(body, list):
        lines = [_help_body_live(line, endtab, maxtab) for line in body]
        lines = body_prepend(lines, '$1')
        return '\\n'.join(lines)
    body = _help_body_live(body, endtab, maxtab)
    return body_prepend(body, '$1')


def convert_snippet_live(snippet: Snippet, prefix: str = '', suffix: str = '',
                         endtab: bool = True) -> Snippet:
    """Convert a snippet from internal to VSCode format.

    Parameters
    ----------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, description.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

    Returns
    -------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, triggerWhenComplete,
        description and priority.
    """
    maxtab = 0
    if not endtab:
        maxtab = count_tabs(snippet['body'])
    live_prefix = convert_trigger_live(snippet['prefix'], prefix, suffix)
    live_body = convert_body_live(snippet['body'], endtab, maxtab)
    return {'prefix': live_prefix, 'body': live_body, 'mode': snippet['mode'],
            'triggerWhenComplete': True, 'description': snippet['description'],
            'priority': len(snippet['prefix'])}


def convert_vscode(snippets: List[Snippet], prefix: str = '', suffix: str = '',
                   endtab: bool = True) -> SnippetDict:
    """Convert list of snippets from internal to VSCode format.

    Parameters
    ----------
    snippets : List[Snippet]
        List of snippet objects: dict with prefix, body, mode, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

    Returns
    -------
    snippets : Dict[str, Snippet]
        Dict of snippet objects: dict with prefix, body, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    """
    vsc_snippets = {}
    for snip in snippets:
        new_snip = convert_snippet_vsc(snip, prefix, suffix, endtab)
        vsc_snippets[snip['description']] = new_snip
    return vsc_snippets


def convert_atom(snippets: List[Snippet], prefix: str = '', suffix: str = '',
                 endtab: bool = True) -> AtomSnippetDict:
    """Convert list of snippets from internal to VSCode format.

    Parameters
    ----------
    snippets : List[Snippet]
        List of snippet objects: dict with prefix, body, mode, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

    Returns
    -------
    snippets : Dict[str, Snippet]
        Dict of dict of snippet objects: dict with prefix, body.
        `Snippet = Dict[str, str] or Dict[str, List[str]]`.
    """
    atom_snippets = {}
    for snip in snippets:
        new_snip = convert_snippet_atom(snip, prefix, suffix, endtab)
        atom_snippets[snip['description']] = new_snip
    return {'.text.tex.latex': atom_snippets}


def convert_live(snippets: List[Snippet],
                 prefix: str = '', suffix: str = '', endtab: bool = True,
                 ) -> List[Snippet]:
    """Convert list of snippets from internal to VSCode format.

    Parameters
    ----------
    snippets : List[Snippet]
        List of snippet objects: dict with prefix, body, mode, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    prefix_m, suffix_m, endtab_m
        Versions of `prefix`, `suffix`, `endtab` for multiline snippets.

    Returns
    -------
    live_snippets : List[Snippet]
        List of snippet objects: dicts with prefix, body, mode,
        triggerWhenComplete, description, priority.
    """
    live_snippets = []
    for snip in snippets:
        new_snip = convert_snippet_live(snip, prefix, suffix, endtab)
        live_snippets.append(new_snip)
    return live_snippets


def convert_split(snippets: List[Snippet],
                  prefix: str = '', suffix: str = '', endtab: bool = True,
                  prefix_m: str = '', suffix_m: str = '', endtab_m: bool = True
                  ) -> (List[Snippet], SnippetDict):
    """Convert list of snippets from internal to live/VSCode format.

    single/multi-line snippets -> live/VSCode format.

    Parameters
    ----------
    snippets : List[Snippet]
        List of snippet objects: dict with prefix, body, mode, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    prefix_m, suffix_m, endtab_m
        Versions of `prefix`, `suffix`, `endtab` for multiline snippets.

    Returns
    -------
    live_snippets : List[Snippet]
        List of single-line snippet objects: dicts with prefix, body, mode,
        triggerWhenComplete, description, priority.
    vsc_snippets : Dict[str, Snippet]
        Dict of multi-line snippets: dicts with prefix, body, description.
    """
    vsc_snippets = {}
    live_snippets = []
    for snip in snippets:
        if isinstance(snip['body'], list):
            new_snip = convert_snippet_vsc(snip, prefix_m, suffix_m, endtab_m)
            vsc_snippets[snip['description']] = new_snip
        else:
            new_snip = convert_snippet_live(snip, prefix, suffix, endtab)
            live_snippets.append(new_snip)
    return live_snippets, vsc_snippets


def read_data_json(file_name: str):
    """Read imported snippet data from json file

    Parameters
    ----------
    file_name : str
        Name of internal `.json` file with snippet info.

    Returns
    -------
    snippets : Dict[str, Snippet]
        List of snippet objects: dicts with prefix, body, mode, description.
        Superset of the info needed by: vscode/latex-utilities/atom snippets
        Derived: `multiline = isinstance(body, list)`, `priority = len(prefix)`
        Type: `Snippet = Dict[str, str]` or `Dict[str, List[str]]`.
    """
    with open(file_name, 'r') as file:
        snippets = json.load(file)
    return snippets


def make_snippet_json(snippets: Union[Snippet, SnippetDict, None] = None,
                      snip_file: str = 'latex.json',
                      live_snippets: Optional[List[Snippet]] = None,
                      live_file: str = 'liveSnippets.json'):
    """Write snippets in the chosen format to .json files.

    Parameters
    ----------
    snippets : Dict[str, Snippet] or Dict[str, Dict[str, Snippet]]
        Dict of (dict of) snippet objects: dict with prefix, body, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    snip_file : str, optional, default: latex.json
        Name of file for normal snippets.
    live_snippets : List[Snippet], optional
        List of single-line snippet objects: dicts with prefix, body, mode,
        triggerWhenComplete, description, priority.
    live_file : str, optional, default: liveSnippets.json
        Name of file for live snippets.
    """
    if snippets is not None:
        with open(snip_file, 'w') as file:
            json.dump(snippets, file, indent=4)
    if live_snippets is not None:
        with open(live_file, 'w') as file:
            json.dump(live_snippets, file, indent=4)


def make_snippet_cson(snippets: Optional[SnippetDict] = None,
                      snip_file: str = 'language-latex.cson'):
    """Write snippets in the chosen format to .json files.

    Parameters
    ----------
    snippets : Dict[str, Dict[str, Snippet]]
        Dict of dict of snippet objects: dict with prefix, body.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    snip_file : str, optional, default: language-latex.cson
        Name of file for normal snippets.
    """
    if snippets is not None:
        with open(snip_file, 'w') as file:
            cson.dump(snippets, file, indent=4)


if __name__ == "__main__":
    snippet_data = read_data_json('data/data.json')
    snips = convert_vscode(snippet_data, prefix=';')
    make_snippet_json(snips)
    snips = convert_atom(snippet_data, prefix=';')
    make_snippet_cson(snips)
    live_snips = convert_live(snippet_data, suffix='  ')
    make_snippet_json(live_snippets=live_snips)
    # live_snips, snips = convert_split(snippet_data, suffix='  ', prefix_m=';')
    # make_snippet_json(snips, live_snippets=live_snips)
